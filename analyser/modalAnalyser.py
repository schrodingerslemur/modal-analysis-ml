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

        self.inplane_modes = inplane_modes
        return inplane_modes
    
    def get_inrange_outplane(self):
        pass
