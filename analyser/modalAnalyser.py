import numpy as np

class ModalAnalyser:
    def __init__(self, 
                 model, 
                 ip_thres=96, 
                 sumxz_thres=1e5, 
                 node_thres=7, 
                 lower_p_thres=0,
                 near_inplane_thres=300
                 ):
        self.model = model
        self.mode_table = model.mode_table_df
        self.max = model.max_modes

        self.ip_thres = ip_thres
        self.node_thres = node_thres
        self.lower_p_thres = lower_p_thres
        self.sumxz_thres = sumxz_thres
        self.near_inplane_thres = near_inplane_thres

        self.inplane_modes = None
        self.near_inplane_modes = None
    
    # n represents mode number
    def get_proportions(self, n):
        mode_df = self.model(n)
        mode_df = mode_df[mode_df['U2'] >= 0].copy()
    
        sq_x = mode_df['U1']**2
        sq_y = mode_df['U2']**2
        sq_z = mode_df['U3']**2
        
        sumsq_x = sq_x.sum()
        sumsq_y = sq_y.sum()
        sumsq_z = sq_z.sum()

        total_energy = sumsq_x + sumsq_y + sumsq_z

        oop = ((sumsq_y) / total_energy) * 100
        ip = ((sumsq_x + sumsq_z) / total_energy) * 100

        return oop, ip, sumsq_x, sumsq_y, sumsq_z
    
    def get_vectors(self, n):
        df = self.model(n, include_node=True)
        R = np.hypot(df['x'], df['z']) # sqrt(x^2 + z^2)
        R_safe = R.replace(0, np.nan)
        
        # Unit r = (x/R, 0, z/R)
        r_hat_x = df['x'] / R_safe
        r_hat_z = df['z'] / R_safe
        
        # Unit n = (0, 1, 0)
        
        # Unit t = unit n x unit r =  (z/R, 0, -x/R)
        t_hat_x = r_hat_z
        t_hat_z = -r_hat_x
        
        # Tangential component = U dot t_hat
        U_t = np.dot(df['U1'], t_hat_x) + np.dot(df['U3'], t_hat_z)
        # Radial component = U dot r_hat
        U_r = np.dot(df['U1'], r_hat_x) + np.dot(df['U3'], r_hat_z)
        # Normal component = U dot n_hat
        U_n = np.sum(df['U2'])


        # Spherical coordinates
        U_rho = np.sqrt(df['U1']**2 + df['U2']**2 + df['U3']**2)
        U_theta = np.arctan(df['U3'] / df['U1']).abs().sum()
        U_phi = np.arctan(df['U2'] / U_rho).abs().sum()

        U_rho = df['U_rho'].sum()

        return U_rho, U_theta, U_phi, U_t, U_r, U_n
    
    def is_tangential(self, n):
        U_rho, U_theta, U_phi, U_t, U_r, U_n = self.get_vectors(n)


    def contains_node(self, n):
        node_thres = self.node_thres
        lower_p_thres = self.lower_p_thres

        mode_df = self.model(n)
        resultant = np.sqrt(mode_df['U1']**2 + mode_df['U2']**2 + mode_df['U3']**2)
        zero_proportion = (resultant < node_thres).sum() / len(mode_df)
        return zero_proportion > lower_p_thres
    
    def get_inplane(self):
        inplane_modes = []

        for n in range(1, self.max + 1):
            oop, ip, x, y, z = self.get_proportions(n)
            if ip > self.ip_thres and x+z > self.sumxz_thres and self.contains_node(n):
                inplane_modes.append(n)

        if self.inplane_modes:
            print("Overwriting previously calculated inplane modes...")
        self.inplane_modes = inplane_modes

        return inplane_modes
    
    def get_inrange_inplane(self) -> set:
        if not self.inplane_modes:
            raise ValueError("In-plane modes have not been calculated. Please run get_inplane() first.")
        
        inrange_outplane = set()

        freqs = self.mode_table.set_index('mode_no')

        for mode in self.inplane_modes:
            curr_freq = freqs.loc[mode].item()
            # Increasing order
            i = 1
            while (mode + i <= self.max) and (freqs.loc[mode + i].item() - curr_freq <= self.near_inplane_thres) and (mode + i not in self.inplane_modes):
                inrange_outplane.add(mode+i)
                i += 1
            
            # Decreasing order
            j = 1
            while (mode - j >= 1) and (curr_freq - freqs.loc[mode-j].item() <= self.near_inplane_thres) and (mode - j not in self.inplane_modes):
                inrange_outplane.add(mode-j)
                j += 1
        
        return sorted(list(inrange_outplane))

