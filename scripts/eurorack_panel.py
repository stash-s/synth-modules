import FootprintWizardBase
import pcbnew

from pcbnew import *


class EurorackPanel(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "Eurorack Panel"
    
    def GetDescription(self):
        return "A panel for Eurorack modules with PCB base andmounting holes."
    
    def GetValue(self):
        return "Eurorack_Panel_{u}_{hp}HP".format(
            hp = self.parameters["Shape"]["HP width"],
            u = "1U" if self.parameters["Shape"]["1U"] else "3U"
        )
    
    def GenerateParameterList(self):
        self.AddParam("Shape", "HP width", self.uInteger, 4)
        self.AddParam("Shape", "1U", self.uBool, False)


    def CheckParameters(self):
        pass

    lookup = {
        1:5.00,2:9.80,3:15.00,4:20.00,5:25.00,6:30.00,7:35.20,8:40.30,9:45.50,10:50.50,
        11:55.50,12:60.60,13:66.60,14:70.80,15:75.90,16:80.90,17:86.00,18:91.30,19:96.20,20:101.30,
        21:106.40,22:111.40,23:116.50,24:121.60,25:126.70,26:131.70,27:136.80,28:141.90,29:147.00,30:152.10,
        31:157.20,32:162.20,33:167.30,34:172.40,35:177.50,36:182.60,37:187.60,38:192.70,39:197.80,40:202.90,
        41:208.00,42:213.00,43:218.10,44:223.20,45:228.30,46:233.30,47:238.40,48:243.50,49:248.60,50:253.70,
        51:258.70,52:263.80,53:268.90,54:274.00,55:279.10,56:284.10,57:289.20,58:294.30,59:299.40,60:304.50,
        61:309.50,62:314.60,63:319.70,64:324.80,65:329.90,66:335.00,67:340.00,68:345.10,69:350.20,70:355.30,
        71:360.40,72:365.40,73:370.50,74:375.60,75:380.70,76:385.70,77:390.80,78:395.90,79:401.00,80:406.10,
        81:411.10,82:416.20,83:421.30,84:426.40,85:431.50,86:436.50,87:441.60,88:446.70,89:451.80,90:456.90,
        91:461.90,92:467.00,93:472.10,94:477.20,95:482.30,96:487.30,97:492.40,98:497.50,99:502.60,100:507.70,
        101:512.70,102:517.80,103:522.90,104:528.00,105:533.10,106:538.10,107:543.20,108:548.30,109:553.40,110:558.50,
        111:563.50,112:568.60,113:573.70,114:578.80,115:583.90,116:588.90,117:594.00,118:599.10,119:604.20,120:609.30,
        121:614.30,122:619.40,123:624.50,124:629.60,125:634.70,126:639.70,127:644.80,128:649.90,129:655.00,130:660.10,
        131:665.10,132:670.20,133:675.30,134:680.40,135:685.50,136:690.50,137:695.60,138:700.70,139:705.80,140:710.90,
        141:715.90,142:721.00,143:726.10,144:731.20,145:736.30,146:741.30,147:746.40,148:751.50,149:756.60,150:761.70,
        151:766.70,152:771.80,153:776.90,154:782.00,155:787.10,156:792.10,157:797.20,158:802.30,159:807.40,160:812.50,
        161:817.50,162:822.60,163:827.70,164:832.80
  }

    def panelWidth(self, hp_width):
        return (7.5 if hp_width == 1.5 else self.lookup[int(hp_width)])  * pcbnew.FromMM(1.0)

    def BuildThisFootprint(self):
        hp_width = self.parameters["Shape"]["HP width"]
        panel_width = self.panelWidth(hp_width)
        panel_height = (39.65 if self.parameters["Shape"]["1U"] else 128.5) * pcbnew.FromMM(1.0)
        pcb_height   = (22.5  if self.parameters["Shape"]["1U"] else 110) * pcbnew.FromMM(1.0) 
        pcb_margin = 0.5 * pcbnew.FromMM(1.0)
        pcb_width  = panel_width - 2 * pcb_margin
        inner_panel_height = pcb_height + 2 * pcb_margin

        self.draw.SetLayer(pcbnew.F_Fab)
        self.draw.SetLineThickness(pcbnew.FromMM(0.1))
        self.draw.Box(0, 0, panel_width, panel_height)
        self.draw.Line(-panel_width/2, -inner_panel_height/2, panel_width/2, -inner_panel_height/2)
        self.draw.Line(-panel_width/2,  inner_panel_height/2, panel_width/2,  inner_panel_height/2)

        _5mm = pcbnew.FromMM(5)
        _3mm = pcbnew.FromMM(3)
        _2mm = pcbnew.FromMM(2)
        _1_5mm = pcbnew.FromMM(1.5)
        _1mm = pcbnew.FromMM(1)

        scale_step = _1mm

        for n in range (0, 1 + int(panel_width / (2 *scale_step))):
            x_pos = n * scale_step
            line_length = _3mm if (n % 10) == 0 else _2mm if (n % 5) == 0 else _1mm
            self.draw.Line(x_pos, - inner_panel_height/2, x_pos, - inner_panel_height/2 - line_length)
            self.draw.Line(x_pos,   inner_panel_height/2, x_pos,   inner_panel_height/2 + line_length)
            if n > 0:
                self.draw.Line(-x_pos,- inner_panel_height/2, -x_pos,- inner_panel_height/2 - line_length)
                self.draw.Line(-x_pos,  inner_panel_height/2, -x_pos,  inner_panel_height/2 + line_length)

        # draw mount holes
        mount_hole_y = int(panel_height / 2.0 -  3 * pcbnew.FromMM(1.0))

        mount_hole_x = 0 
        
        if hp_width == 2:
            mount_hole_x = -2.5 * pcbnew.FromMM(1.0)
        elif hp_width < 6:
            mount_hole_x = int (panel_width  / 2.0 - 7.5 * pcbnew.FromMM(1.0))
        else:
            mount_hole_x = - int(((hp_width - 3) * 5.08 / 2) * pcbnew.FromMM(1.0))

        if hp_width >=6:
            self.draw.Circle( mount_hole_x, mount_hole_y, 3.2 / 2 * pcbnew.FromMM(1.0))
            self.draw.Circle( mount_hole_x, -mount_hole_y, 3.2 / 2 * pcbnew.FromMM(1.0))

        self.draw.Circle(-mount_hole_x, mount_hole_y, 3.2 / 2 * pcbnew.FromMM(1.0))
        self.draw.Circle(-mount_hole_x, -mount_hole_y, 3.2 / 2 * pcbnew.FromMM(1.0))

        self.draw.SetLayer(pcbnew.Edge_Cuts)
        self.draw.SetLineThickness(pcbnew.FromMM(0.05))
        self.draw.Box(0, 0, pcb_width, pcb_height)
        

EurorackPanel().register()