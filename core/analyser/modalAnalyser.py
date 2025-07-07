import numpy as np
import pandas as pd
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
        self.mode_table = model.mode_table_df.set_index('mode_no')
        self.max = model.max_modes

        self.oop_thres = oop_thres
        self.near_inplane_thres = near_inplane_thres

        self.inplane_modes = None
        self.outplane_modes = None

    def get_freq(self, n: int) -> float:
        return self.mode_table.loc[n].item()
    
    def get_proportions(self, n: int) -> tuple[float, float, float, float, float, float]:
        """
        Gets specific proportions from a specific mode.

        Parameters:
        n (int): The mode number to analyze.

        Returns:
        tuple: A tuple containing the out-of-plane proportion, in-plane proportion, and the squared displacements.
            oop: out-of-plane proportion - y^2 / (y^2 + x^2 + z^2)
            ip: in-plane proportion - (x^2 + z^2) / (y^2 + x^2 + z^2)
            sq_x: squared displacement in x-direction
            sq_y: squared displacement in y-direction
            sq_z: squared displacement in z-direction
            resultant: resultant displacement
        """
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

    def is_tangential(self, n: int, tang_ratio_thres: float = 2.0) -> bool:
        """
        Checks if the mode is tangential. Calculates the tangential-to-radial displacement ratio.
        Takes radial, normal and tangential unit vectors, then computes the displacement components.

        Parameters:
        n (int): The mode number to analyze.
        tang_ratio_thres (float): The threshold ratio to determine if the mode is tangential. Default is 2.0.

        Returns:
        bool: True if the mode is tangential, False otherwise.
        """
        df = self.model(n)
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

    def is_rigid_rotation(self, n: int, rigid_ratio_thres: float = 0.1, return_ratio: bool = False) -> bool:
        """
        Checks if the mode is undergoing rigid body rotation. Some modes move in one continuous clockwise/anti-clockwise motion -
        we want to remove these modes from our analysis.

        Parameters:
        n (int): The mode number to analyze.
        rigid_ratio_thres (float): The threshold ratio to determine if the mode is undergoing rigid body rotation. Default is 0.1.
        return_ratio (bool): Whether to return the rotation ratio instead of just True/False. Default is False.

        Returns:
        bool: True if the mode is undergoing rigid body rotation, False otherwise.
        """
        df = self.model(n)

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

    def get_inplane(self) -> list[int]:
        """
        Get the list of in-plane mode numbers. This is achieved if modes achieve these criterias:
            1. Tangential
            2. Not undergoing rigid body rotation
            3. In-plane displacement is significant (greater than twice the mean)

        Returns:
        list[int]: The list of in-plane mode numbers.
        """
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
    
    
    def get_outplane(self) -> list[int]:
        """
        Gets all outplane modes in the specified range.
        """
        outplane_modes = []
        for mode in range(1, self.max + 1):
            oop, _, _, _, _, _ = self.get_proportions(mode)
            if oop > self.oop_thres:
                outplane_modes.append(mode)
        self.outplane_modes = outplane_modes
        return outplane_modes

    def get_results(self) -> bool:
        """
        Check the modal properties and classify modes into in-plane, near in-plane, and out-of-plane.
        Ensures that out-of-plane modes are not within the specified near-in-plane threshold.

        Returns:
        bool: True if out-of-plane modes are not within the specified near-in-plane threshold, False otherwise.
        """
        if not self.inplane_modes:
            self.get_inplane()

        # Just for reference
        self.get_outplane()

        print("In-plane modes:", self.inplane_modes)
        print("Out-of-plane modes:", self.outplane_modes)

        self.results = self.results_table()
        print("Results Table:")
        print(self.results)

        if (self.results["Lower Frequency Diff (Hz)"].min() < self.near_inplane_thres or self.results["Upper Frequency Diff (Hz)"].min() < self.near_inplane_thres):
            print("Warning: Some out-of-plane modes are near in-plane modes.")
            return False
        return True

    def results_table(self) -> 'html':
        inplane_outplane_tuple = []

        for inplane_mode in self.inplane_modes:
            # Find nearest out-of-plane modes to the left and right
            left = max([m for m in self.outplane_modes if m < inplane_mode], default=None)
            right = min([m for m in self.outplane_modes if m > inplane_mode], default=None)

            left_freq = self.get_freq(left) if left is not None else None
            inplane_freq = self.get_freq(inplane_mode)
            right_freq = self.get_freq(right) if right is not None else None
            left_diff = np.nan if left_freq is None else inplane_freq - left_freq
            right_diff = np.nan if right_freq is None else right_freq - inplane_freq

            inplane_outplane_tuple.append((left_diff, left_freq, inplane_freq, right_freq, right_diff))

        df = pd.DataFrame(inplane_outplane_tuple, columns=["Lower Frequency Diff (Hz)", "Lower Out-of-plane (Hz)", "In-plane (Hz)", "Right Out-of-plane (Hz)", "Upper Frequency Diff (Hz)"])
        return df

