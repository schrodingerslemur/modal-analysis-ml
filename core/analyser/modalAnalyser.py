import numpy as np
from core.parser.modalParser import ModalParser # safe to remove

class ModalAnalyser:
    def __init__(self, model: ModalParser, oop_thres: int = 90, near_inplane_thres: int = 300) -> 'ModalAnalyser':
        """
        Initializes Modal Analyser class.

        Parameters:
        model (ModalParser): 
            The modal parser instance.
        oop_thres (int): 
            Out-of-plane threshold. 
            This threshold determines the minimum out-of-plane proportion required to classify a mode as out-of-plane.
        near_inplane_thres (int): 
            Near in-plane threshold. 
            This threshold determines how close an out-of-plane should not be to an in-plane mode.
        """
        
        self.model = model
        self.mode_table = model.mode_table_df
        self.max = model.max_modes

        self.oop_thres = oop_thres
        self.near_inplane_thres = near_inplane_thres

        self.inplane_modes = None
        self.near_inplane = None
        self.outplane_modes = None
    
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

        resultant = np.sqrt(sq_x + sq_y + sq_z).sum()

        total_energy = (sumsq_x + sumsq_y + sumsq_z)

        oop = ((sumsq_y) / total_energy) * 100
        ip = ((sumsq_x + sumsq_z) / total_energy) * 100

        return oop, ip, sumsq_x, sumsq_y, sumsq_z, resultant
    
    def is_tangential(self, n, tang_ratio_thres=2.0): 
        df = self.model(n, include_node=True)
        ctr_x = df.x.mean()
        ctr_z = df.z.mean()
        
        r_vec   = np.stack([df.x-ctr_x, 0*df.x, df.z-ctr_z]).T
        r_len   = np.linalg.norm(r_vec, axis=1)
        r_hat   = (r_vec.T / r_len).T                       # shape (N,3)
        t_hat   = np.cross(np.array([0,1,0]), r_hat)        # (N,3)

        U  = np.stack([df.U1, df.U2, df.U3]).T         
        u_r = np.sum(U * r_hat, axis=1)             
        u_t = np.sum(U * t_hat, axis=1)

        Er  = np.sum(u_r**2)
        Et  = np.sum(u_t**2)
        ratio = Et / Er

        if ratio > tang_ratio_thres:
            return True
        elif ratio < 1/tang_ratio_thres:
            return False
        else:
            return False

    def is_rigid_rotation(self, n, rigid_ratio_thres=0.1, return_ratio=False):
        df = self.model(n, include_node=True)

        ctr_x = df['x'].mean()
        ctr_z = df['z'].mean()

        # local unit tangential vector t̂ = n̂ × r̂ (n̂ = +Y)
        rx = df['x'] - ctr_x
        rz = df['z'] - ctr_z
        r_len = np.hypot(rx, rz)
        t_hat_x =  np.nan_to_num( rz / r_len)
        t_hat_z = -np.nan_to_num( rx / r_len)

        # tangential component
        u_t = df['U1']*t_hat_x + df['U3']*t_hat_z

        rms  = np.sqrt(np.mean(u_t**2))
        rho  = 0.0 if rms == 0 else abs(np.mean(u_t)) / rms

        flag = bool(rho > rigid_ratio_thres)
        return (flag, float(rho)) if return_ratio else flag
    
    def get_inplane(self):
        inplane_modes = []
        xz = []

        # Ensure is tangential and not rigid motion
        for n in range(1, self.max + 1):
            _, _, x, _, z, _ = self.get_proportions(n)
            xz.append(x+z)
            if self.is_tangential(n) and not self.is_rigid_rotation(n): 
                inplane_modes.append(n)

        # Ensure all x+z are > 2 * mean(x+z)
        xz_mean = np.mean(xz)
        inplane_modes = [mode for mode in inplane_modes if self.get_proportions(mode)[2] + self.get_proportions(mode)[4] > 2*xz_mean]

        if self.inplane_modes:
            print("Overwriting previously calculated inplane modes...")
        self.inplane_modes = inplane_modes

        return inplane_modes
    
    def get_near_inplane(self) -> set:
        if not self.inplane_modes:
            raise ValueError("In-plane modes have not been calculated. Please run get_inplane() first.")
        
        near_inplane = set()

        freqs = self.mode_table.set_index('mode_no')

        for mode in self.inplane_modes:
            curr_freq = freqs.loc[mode].item()
            # Increasing order
            i = 1
            while (mode + i <= self.max) and (freqs.loc[mode + i].item() - curr_freq <= self.near_inplane_thres) and (mode + i not in self.inplane_modes):
                near_inplane.add(mode+i)
                i += 1
            
            # Decreasing order
            j = 1
            while (mode - j >= 1) and (curr_freq - freqs.loc[mode-j].item() <= self.near_inplane_thres) and (mode - j not in self.inplane_modes):
                near_inplane.add(mode-j)
                j += 1
        
        if self.near_inplane:
            print("Overwriting previously calculated NEAR inplane modes")

        self.near_inplane = sorted(list(near_inplane))
        return self.near_inplane
    
    def is_outplane(self, n: int) -> bool:
        oop, _, _, _, _, _ = self.get_proportions(n)
        if oop > self.oop_thres:
            return True
        return False
    
    def check(self) -> bool:
        if not self.inplane_modes:
            self.get_inplane()
        
        print("In-plane modes:", self.inplane_modes)

        if not self.near_inplane:
            self.get_near_inplane()

        print("Near in-plane modes:", self.near_inplane)

        self.outplane_modes = []
        for potential_oop in self.near_inplane:
            if self.is_outplane(potential_oop):
                self.outplane_modes.append(potential_oop)

        print("Out-of-plane modes:", self.outplane_modes)
        if len(self.outplane_modes) > 0:
            return False
        return True
