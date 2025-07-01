import numpy as np

class ModalAnalyser:
    def __init__(self, 
                 model, 
                 ip_thres=96, 
                 oop_thres=90,
                 sumxz_thres=1e5, 
                 min_res_thres=2,
                 node_thres=7, 
                 lower_p_thres=0,
                 near_inplane_thres=300
                 ):
        self.model = model
        self.mode_table = model.mode_table_df
        self.max = model.max_modes

        self.ip_thres = ip_thres
        self.oop_thres = oop_thres
        self.node_thres = node_thres
        self.lower_p_thres = lower_p_thres
        self.min_res_thres = min_res_thres
        self.sumxz_thres = sumxz_thres
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
    
    def get_vectors(self, n, spherical_only=False):
        if spherical_only:
            df = self.model(n)
        else:
            df = self.model(n, include_node=True)

        U_rho = np.sqrt(df['U1']**2 + df['U2']**2 + df['U3']**2)
        U_theta = np.arctan2(df['U3'], df['U1']).abs().sum()
        U_phi = np.arctan2(df['U2'], U_rho).abs().sum()
        U_rho_sum = U_rho.sum()

        if spherical_only:
            print(f"U_rho: {U_rho_sum}, U_theta: {U_theta}, U_phi: {U_phi}")
            print(f"U_theta / (U_theta + U_rho): {U_theta*100 / (U_theta + U_rho_sum)}")
            return U_rho_sum, U_theta, U_phi
        else:
            R = np.hypot(df['x'], df['z'])  # sqrt(x^2 + z^2)
            R_safe = R.replace(0, np.nan)

            # Unit r = (x/R, 0, z/R)
            r_hat_x = df['x'] / R_safe
            r_hat_z = df['z'] / R_safe

            # Unit t = unit n x unit r =  (z/R, 0, -x/R)
            t_hat_x = r_hat_z
            t_hat_z = -r_hat_x

            # Tangential component = U dot t_hat
            U_t = np.dot(df['U1'], t_hat_x.fillna(0)) + np.dot(df['U3'], t_hat_z.fillna(0))
            # Radial component = U dot r_hat
            U_r = np.dot(df['U1'], r_hat_x.fillna(0)) + np.dot(df['U3'], r_hat_z.fillna(0))
            # Normal component = U dot n_hat
            U_n = np.sum(df['U2'].abs())

            print(f"U_rho: {U_rho_sum}, U_theta: {U_theta}, U_phi: {U_phi}, U_t: {U_t}, U_r: {U_r}, U_n: {U_n}")
            return U_rho_sum, U_theta, U_phi, U_t, U_r, U_n

    def get_min_resultant(self, n: int):
        df = self.model(n)
        resultant = np.hypot(df['U1'], df['U3'])
        return resultant.min()
    
    def is_tangential(self, n, tang_ratio_thres=2.0):          # Et/Er threshold
        node_df = self.model(1, include_node=True)

        ctr_x = node_df.x.mean()
        ctr_z = node_df.z.mean()
        
        r_vec   = np.stack([node_df.x-ctr_x, 0*node_df.x, node_df.z-ctr_z]).T
        r_len   = np.linalg.norm(r_vec, axis=1)
        r_hat   = (r_vec.T / r_len).T                       # shape (N,3)
        t_hat   = np.cross(np.array([0,1,0]), r_hat)        # (N,3)

        df = self.model(n)     
        U  = np.stack([df.U1, df.U2, df.U3]).T         
        u_r = np.sum(U * r_hat, axis=1)             
        u_t = np.sum(U * t_hat, axis=1)

        Er  = np.sum(u_r**2)
        Et  = np.sum(u_t**2)
        ratio = Et / Er

        # print(n, ratio)
        if ratio > tang_ratio_thres:
            return True
        elif ratio < 1/tang_ratio_thres:
            return False
        else:
            return False

    def is_rigid_rotation(self, n,
                      ctr_x=0.0, ctr_z=0.0,
                      rigid_ratio_thres=0.1,
                      return_ratio=False):
        """
        True  → every rim node moves tangentially in the *same* direction
                (clockwise or anti-clockwise)  ⇒ rigid-body whirl.

        Parameters
        ----------
        model : callable
            model(n, include_node=True) must return a DataFrame with columns
            x, y, z, U1, U2, U3 (same node order for every mode).
        n : int
            Mode number to test.
        ctr_x, ctr_z : float
            X-Z coordinates of the rotor centre.
        rigid_ratio_thres : float
            Threshold for  ρ = |mean(u_t)| / rms(u_t).
            ρ ≈ 1 ⇒ rigid rotation,  ρ ≈ 0 ⇒ standing wave.
        return_ratio : bool
            If True also return the computed ρ.

        Returns
        -------
        bool   (and optionally float)
            Flag indicating rigid rotation  (and the value of ρ if requested).
        """
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
    
    def contains_node(self, n):
        node_thres = self.node_thres
        lower_p_thres = self.lower_p_thres

        mode_df = self.model(n)
        resultant = np.sqrt(mode_df['U1']**2 + mode_df['U2']**2 + mode_df['U3']**2)
        zero_proportion = (resultant < node_thres).sum() / len(mode_df)
        return zero_proportion > lower_p_thres
    
    def get_inplane(self, tangential=False):
        inplane_modes = []

        if not tangential:
            print('not tangential')
            for n in range(1, self.max + 1):
                oop, ip, x, y, z, _ = self.get_proportions(n)
                if ip > self.ip_thres and x+z > self.sumxz_thres and self.contains_node(n) and self.is_tangential(n):
                    inplane_modes.append(n)
        else:
            print('tangential')
            xz = []
            for n in range(1, self.max + 1):
                oop, ip, x, y, z, res = self.get_proportions(n)
                xz.append(x+z)
                if self.is_tangential(n) and (print(n, "x+z:", x+z) or True): # TODO: ideal: 350000  or x+z > 200000
                    flag, rho =  self.is_rigid_rotation(n, return_ratio=True)
                    if not flag:
                        # print(f"Mode {n}: x={x}, y={y}, z={z}, x+z: {x+z}")
                        # print(f"rho: {rho}, res: {res}")
                        inplane_modes.append(n)
                        # xz.append(x+z)
            xz_mean = np.mean(xz)
            print("xz_mean:", xz_mean)
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
        oop, ip, x, y, z, _ = self.get_proportions(n)
        if oop > self.oop_thres:
            print(n, 'oop:', oop, "failed")
            return True
        print(n, 'oop:', oop, "passed")
        return False
    
    def check(self, tangential=False) -> bool:
        if not self.inplane_modes:
            self.get_inplane(tangential=tangential)
        
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


    ## HELPER:
    def iterate(self, func, params=None, modes=None) -> None:
        if modes is None:
            modes = range(1, self.max + 1)
        for n in modes:
            print(n)
            if params is not None:
                if isinstance(params, dict):
                    func(n, **params)
                elif isinstance(params, (list, tuple)):
                    func(n, *params)
                else:
                    func(n, params)
            else:
                func(n)
    