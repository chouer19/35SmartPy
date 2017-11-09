#msg for CAN of 35 smart car
#ID: 0x199, read this gun message from CAN
class gun_read:
    def __init__(self, control_mode=0x00 , control_depth=0x00 , left_speed=0x00 , right_speed=0x00 ):
        #byte[0] 0:manual control, 1: pc control
        self.control_mode = control_mode
        #byte[1] control depth
        self.control_depth = control_depth
        #byte[2] & byte[3],left speed
        self.left_speed = left_speed
        #byte[4] & byte[5],left speed
        self.right_speed = right_speed
        pass

#ID: 0x200, send this gun message to CAN
class gun_send:
    def __init__(self, control_mode = 0x00 , control_depth = 0x00 ):
        #byte[0] control mode, 0:manual control, 1:pc control
        self.control_mode = control_mode
        #byte[1] control depth
        self.control_depth = controle_depth
        pass

#ID: 0X100, read this brake message from CAN
class brake_read:
    def __init__(self, motor_time=0x0000 , estop_status=0x00 , button_status=0x00 , pedal_status=0x00 , can_status=0x00 , remote_control=0x00 , real_status=0x00 ):
        # byte[0] & byte[1], time of brake-motor runing 0x00  0x00 0x00 , time = byte[0x00 ] * 256 + byte[1]
        self.motor_time = motor_time
        # byte[2], if the brake button is pressed down 0x00 , 0x00  is false and 1 is true
        self.button_status = button_status
        # byte[3], if the remote brake control is pressed down 0x00 , 0x00 is false and 1 is true
        self.remote_status = remote_status
        # byte[4], if the pedal is pressed down 0x00 ,
        self.pedal_status = pedal_status
        # byte[5], if the can send brake message 0x00 ,
        self.can_status = can_status
        # byte[6], reserve for the pc, reverse once remote control is pressed down
        self.remote_control = remote_control
        # byte[7], real status of brake, effect of brake
        self.real_status = real_status
        pass

#ID: 0x99, send this message of brake to CAN
class brake_send:
    def __init__(self, control_mode=0x00 , control_depth=0x00 ):
        #byte[0], 0:start braking, 1:stop braking
        self.control_mode = control_mode
        #byte[1], control depth
        self.control_depth = control_depth

#ID: 0x401, read this steer message from CAN
class steer_read:
    def __init__(self, control_mode=0x00 , torque= 0x00 , exception= 0x00 , angle_h= 0x00 , angle_l= 0x00 , steer_calib= 0x00 , check= 0x00 ):
        #byte[0], 0x00:stop control, 0x10: manul control, 0x20: pc control, 0x55: xor check error
        self.control_mode = control_mode
        #byte[1], torque
        self.torque = torque
        #byte[2], error message
        #0x21    0x22    0x23    0x24    0x25    0x26
        #0x32    0x34    0x35
        #0x31
        self.exception = exception
        #byte[3]
        self.angle_h = self.angle_h
        #byte[4], angle = byte[3] * 256 + byte[4] - 1024
        self.angle_l = self.angle_l
        #byte[5], no, done, failed, success
        self.steer_calib = steer_calib
        #byte[7], xor check
        self.check = check

class steer_send:
    def __init__(self, control_mode= 0x00, angle_h = 0x00, angle_l= 0x00 , angle_calib= 0x00 , check= 0x00 ):
        #byte[0], 0x00:stop control, 0x10:manual control, 0x20:pc control
        self.control_mode = control_mode
        #byte[3]
        self.angle_h = angle_h
        #byte[4]
        self.angle_l = angle_l
        #byte[5], 0x55, only worked when manual control
        self.angle_calib = angle_calib
        #byte[7], xor check
        self.check = check
