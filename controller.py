import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def get_steering_controller():
    # New Antecedent/Consequent objects hold universe variables and membership
    # functions
    deviation = ctrl.Antecedent(np.arange(0, 101, 1), 'deviation')
    steering = ctrl.Consequent(np.arange(0, 101, 1), 'steering')

    deviation['farleft'] = fuzz.trapmf(deviation.universe, [0, 0, 25, 40])
    deviation['left'] = fuzz.trimf(deviation.universe, [25, 40, 50])
    deviation['middle'] = fuzz.trimf(deviation.universe, [40,50,60])
    deviation['right'] = fuzz.trimf(deviation.universe, [50,60,75])
    deviation['farright'] = fuzz.trapmf(deviation.universe, [ 60,75,100,100])

    steering['farleft'] = fuzz.trapmf(steering.universe, [0, 0, 25, 40])
    steering['left'] = fuzz.trimf(steering.universe, [25, 40, 50])
    steering['middle'] = fuzz.trimf(steering.universe, [40,50,60])
    steering['right'] = fuzz.trimf(steering.universe, [50,60,75])
    steering['farright'] = fuzz.trapmf(steering.universe, [ 60,75,100,100])

    rule1 = ctrl.Rule(deviation['farleft'], steering['farright'])
    rule2 = ctrl.Rule(deviation['left'], steering['right'])
    rule3 = ctrl.Rule(deviation['middle'], steering['middle'])
    rule4 = ctrl.Rule(deviation['right'], steering['left'])
    rule5 = ctrl.Rule(deviation['farright'], steering['farleft'])
    steering_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])

    steering_controller = ctrl.ControlSystemSimulation(steering_ctrl)
    return steering_controller

def get_speed_controller():
    # New Antecedent/Consequent objects hold universe variables and membership
    # functions

    lightstatus = ctrl.Antecedent(np.arange(0, 101, 1), 'lightstatus')
    lightstatus['green'] = fuzz.trapmf(lightstatus.universe, [0, 0, 25, 40])
    lightstatus['less_green'] = fuzz.trimf(lightstatus.universe, [33, 42, 54])
    lightstatus['yellow'] = fuzz.trimf(lightstatus.universe, [46,54,71])
    lightstatus['red'] = fuzz.trapmf(lightstatus.universe, [63,67,83,90])
    lightstatus['less_red'] = fuzz.trapmf(lightstatus.universe, [ 83,90,100,100])

    distance = ctrl.Antecedent(np.arange(0, 101, 1), 'distance')
    distance['near'] = fuzz.trapmf(distance.universe, [0, 0, 5, 20])
    distance['medium'] = fuzz.trapmf(distance.universe, [5, 10, 25, 35])
    distance['far'] = fuzz.trapmf(distance.universe, [20,35,100,100])


    deviation = ctrl.Antecedent(np.arange(0, 101, 1), 'deviation')
    deviation['farleft'] = fuzz.trapmf(deviation.universe, [0, 0, 25, 40])
    deviation['left'] = fuzz.trimf(deviation.universe, [25, 40, 50])
    deviation['middle'] = fuzz.trimf(deviation.universe, [40,50,60])
    deviation['right'] = fuzz.trimf(deviation.universe, [50,60,75])
    deviation['farright'] = fuzz.trapmf(deviation.universe, [ 60,75,100,100])

    speed = ctrl.Consequent(np.arange(0, 101, 1), 'speed')
    speed['stop'] = fuzz.trapmf(speed.universe, [0, 0, 0, 5])
    speed['slower'] = fuzz.trimf(speed.universe, [3, 25, 50])
    speed['slow'] = fuzz.trimf(speed.universe, [30,60,80])
    speed['medium'] = fuzz.trapmf(speed.universe, [70,90,100,100])

    rule1 = ctrl.Rule(lightstatus['green'] & deviation['middle'], speed['medium'])
    rule2 = ctrl.Rule(lightstatus['green'] & deviation['left'], speed['slow'])
    rule3 = ctrl.Rule(lightstatus['green'] & deviation['right'], speed['slow'])
    rule4 = ctrl.Rule(lightstatus['green'] & deviation['farleft'], speed['slower'])
    rule5 = ctrl.Rule(lightstatus['green'] & deviation['farright'], speed['slower'])

    rule6 = ctrl.Rule(distance['far'] & deviation['middle'], speed['medium'])
    rule7 = ctrl.Rule(distance['far'] & deviation['left'], speed['slow'])
    rule8 = ctrl.Rule(distance['far'] & deviation['right'], speed['slow'])
    rule9 = ctrl.Rule(distance['far'] & deviation['farleft'], speed['slower'])
    rule10 = ctrl.Rule(distance['far'] & deviation['farright'], speed['slower'])

    rule11 = ctrl.Rule(lightstatus['yellow'] & distance['medium'] & deviation['middle'], speed['slow'])
    rule12 = ctrl.Rule(lightstatus['yellow'] & distance['medium'] & deviation['left'], speed['slower'])
    rule13 = ctrl.Rule(lightstatus['yellow'] & distance['medium'] & deviation['right'], speed['slower'])
    rule14 = ctrl.Rule(lightstatus['yellow'] & distance['medium'] & deviation['farleft'], speed['slower'])
    rule15 = ctrl.Rule(lightstatus['yellow'] & distance['medium'] & deviation['farright'], speed['slower'])

    rule16 = ctrl.Rule(lightstatus['yellow'] & distance['near'], speed['stop'])

    rule17 = ctrl.Rule(lightstatus['red'] & distance['medium'] & deviation['middle'], speed['slow'])
    rule18 = ctrl.Rule(lightstatus['red'] & distance['medium'] & deviation['left'], speed['slower'])
    rule19 = ctrl.Rule(lightstatus['red'] & distance['medium'] & deviation['right'], speed['slower'])
    rule20 = ctrl.Rule(lightstatus['red'] & distance['medium'] & deviation['farleft'], speed['slower'])
    rule21 = ctrl.Rule(lightstatus['red'] & distance['medium'] & deviation['farright'], speed['slower'])

    rule22 = ctrl.Rule(lightstatus['red'] & distance['near'], speed['stop'])

    rule23 = ctrl.Rule(lightstatus['less_green'] & distance['medium'] & deviation['middle'], speed['medium'])
    rule24 = ctrl.Rule(lightstatus['less_green'] & distance['medium'] & deviation['left'], speed['slow'])
    rule25 = ctrl.Rule(lightstatus['less_green'] & distance['medium'] & deviation['right'], speed['slow'])
    rule26 = ctrl.Rule(lightstatus['less_green'] & distance['medium'] & deviation['farleft'], speed['slower'])
    rule27 = ctrl.Rule(lightstatus['less_green'] & distance['medium'] & deviation['farright'], speed['slower'])

    rule28 = ctrl.Rule(lightstatus['less_green'] & distance['near'] & deviation['middle'], speed['slower'])
    rule29 = ctrl.Rule(lightstatus['less_green'] & distance['near'] & deviation['left'], speed['slower'])
    rule30 = ctrl.Rule(lightstatus['less_green'] & distance['near'] & deviation['right'], speed['slower'])
    rule31 = ctrl.Rule(lightstatus['less_green'] & distance['near'] & deviation['farleft'], speed['stop'])
    rule32 = ctrl.Rule(lightstatus['less_green'] & distance['near'] & deviation['farright'], speed['stop'])

    rule33 = ctrl.Rule(lightstatus['less_red'] & distance['medium'] & deviation['middle'], speed['slow'])
    rule34 = ctrl.Rule(lightstatus['less_red'] & distance['medium'] & deviation['left'], speed['slower'])
    rule35 = ctrl.Rule(lightstatus['less_red'] & distance['medium'] & deviation['right'], speed['slower'])
    rule36 = ctrl.Rule(lightstatus['less_red'] & distance['medium'] & deviation['farleft'], speed['slower'])
    rule37 = ctrl.Rule(lightstatus['less_red'] & distance['medium'] & deviation['farright'], speed['slower'])

    rule38 = ctrl.Rule(lightstatus['less_red'] & distance['near'], speed['slower'])

    speed_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5,
                                    rule6, rule7, rule8, rule9, rule10,
                                    rule11, rule12, rule13, rule14, rule15,
                                    rule16, rule17, rule18, rule19, rule20,
                                    rule21, rule22, rule23, rule24, rule25,
                                    rule26, rule27, rule28, rule29, rule30,
                                    rule31, rule32, rule33, rule34, rule35,
                                    rule36, rule37, rule38])
    speed_controller = ctrl.ControlSystemSimulation(speed_ctrl)
    return speed_controller

def get_obstacle_controller():

    distance = ctrl.Antecedent(np.arange(0, 101, 1), 'distance')
    distance['very_close'] = fuzz.trapmf(distance.universe, [0, 0, 5, 20])
    distance['close'] = fuzz.trapmf(distance.universe, [10, 15, 35, 45])
    distance['medium'] = fuzz.trapmf(distance.universe, [30,40,50,60])
    distance['far'] = fuzz.trapmf(distance.universe, [50,60,100,100])

    deviation = ctrl.Antecedent(np.arange(0, 101, 1), 'deviation')
    deviation['farleft'] = fuzz.trapmf(deviation.universe, [0, 0, 25, 40])
    deviation['left'] = fuzz.trimf(deviation.universe, [25, 40, 50])
    deviation['middle'] = fuzz.trimf(deviation.universe, [40,50,60])
    deviation['right'] = fuzz.trimf(deviation.universe, [50,60,75])
    deviation['farright'] = fuzz.trapmf(deviation.universe, [ 60,75,100,100])

    obstacle_deviation = ctrl.Antecedent(np.arange(0, 101, 1), 'obstacle_deviation')
    obstacle_deviation['farleft'] = fuzz.trapmf(obstacle_deviation.universe, [0, 0, 25, 40])
    obstacle_deviation['left'] = fuzz.trapmf(obstacle_deviation.universe, [25, 40, 45, 55])
    obstacle_deviation['right'] = fuzz.trapmf(obstacle_deviation.universe, [45,55,60, 75])
    obstacle_deviation['farright'] = fuzz.trapmf(obstacle_deviation.universe, [ 60,75,100,100])

    speed = ctrl.Consequent(np.arange(0, 101, 1), 'speed')
    speed['stop'] = fuzz.trapmf(speed.universe, [0, 0, 0, 5])
    speed['slower'] = fuzz.trimf(speed.universe, [3, 25, 50])
    speed['slow'] = fuzz.trimf(speed.universe, [30,60,80])
    speed['medium'] = fuzz.trapmf(speed.universe, [70,90,100,100])

    steering = ctrl.Consequent(np.arange(0, 101, 1), 'speed')
    steering['farleft'] = fuzz.trapmf(steering.universe, [0, 0, 25, 40])
    steering['left'] = fuzz.trimf(steering.universe, [25, 40, 50])
    steering['middle'] = fuzz.trimf(steering.universe, [40,50,60])
    steering['right'] = fuzz.trimf(steering.universe, [50,60,75])
    steering['farright'] = fuzz.trapmf(steering.universe, [ 60,75,100,100])

    rule1 = ctrl.Rule(distance['far'] & deviation['farleft'], (steering['farright'], speed['medium']))
    rule2 = ctrl.Rule(distance['far'] & deviation['left'], (steering['right'], speed['medium']))
    rule3 = ctrl.Rule(distance['far'] & deviation['middle'], (steering['middle'], speed['medium']))
    rule4 = ctrl.Rule(distance['far'] & deviation['right'], (steering['left'] , speed['medium']))
    rule5 = ctrl.Rule(distance['far'] & deviation['farright'], (steering['farleft'] , speed['medium']))

    rule6 = ctrl.Rule(distance['medium'] & obstacle_deviation['farleft'] & deviation['farleft'], (steering['farright'] , speed['slow']))
    rule7 = ctrl.Rule(distance['medium'] & obstacle_deviation['farleft'] & deviation['left'], (steering['right'] , speed['slow']))
    rule8 = ctrl.Rule(distance['medium'] & obstacle_deviation['farleft'] & deviation['middle'], (steering['right'] , speed['slow']))
    rule9 = ctrl.Rule(distance['medium'] & obstacle_deviation['farleft'] & deviation['right'], (steering['middle'] , speed['slow']))
    rule10 = ctrl.Rule(distance['medium'] & obstacle_deviation['farleft'] & deviation['farright'], (steering['left'] , speed['slow']))

    rule11 = ctrl.Rule(distance['medium'] & obstacle_deviation['left'] & deviation['farleft'], (steering['right'] , speed['slow']))
    rule12 = ctrl.Rule(distance['medium'] & obstacle_deviation['left'] & deviation['left'], (steering['right'] , speed['slow']))
    rule13 = ctrl.Rule(distance['medium'] & obstacle_deviation['left'] & deviation['middle'], (steering['right'] , speed['slow']))
    rule14 = ctrl.Rule(distance['medium'] & obstacle_deviation['left'] & deviation['right'], (steering['middle'] , speed['slow']))
    rule15 = ctrl.Rule(distance['medium'] & obstacle_deviation['left'] & deviation['farright'], (steering['middle'] , speed['slow']))
 
    rule16 = ctrl.Rule(distance['medium'] & obstacle_deviation['right'] & deviation['farleft'], (steering['middle'] , speed['slow']))
    rule17 = ctrl.Rule(distance['medium'] & obstacle_deviation['right'] & deviation['left'], (steering['middle'] , speed['slow']))
    rule18 = ctrl.Rule(distance['medium'] & obstacle_deviation['right'] & deviation['middle'], (steering['left'] , speed['slow']))
    rule19 = ctrl.Rule(distance['medium'] & obstacle_deviation['right'] & deviation['right'], (steering['left'] , speed['slow']))
    rule20 = ctrl.Rule(distance['medium'] & obstacle_deviation['right'] & deviation['farright'], (steering['left'] , speed['slow']))

    rule21 = ctrl.Rule(distance['medium'] & obstacle_deviation['farright'] & deviation['farleft'], (steering['right'] , speed['slow']))
    rule22 = ctrl.Rule(distance['medium'] & obstacle_deviation['farright'] & deviation['left'], (steering['middle'] , speed['slow']))
    rule23 = ctrl.Rule(distance['medium'] & obstacle_deviation['farright'] & deviation['middle'], (steering['left'] , speed['slow']))
    rule24 = ctrl.Rule(distance['medium'] & obstacle_deviation['farright'] & deviation['right'], (steering['left'] , speed['slow']))
    rule25 = ctrl.Rule(distance['medium'] & obstacle_deviation['farright'] & deviation['farright'], (steering['farleft'] , speed['slow']))

    rule26 = ctrl.Rule(distance['close'] & obstacle_deviation['farleft'] & deviation['farleft'], (steering['farright'] , speed['slower']))
    rule27 = ctrl.Rule(distance['close'] & obstacle_deviation['farleft'] & deviation['left'], (steering['right'] , speed['slower']))
    rule28 = ctrl.Rule(distance['close'] & obstacle_deviation['farleft'] & deviation['middle'], (steering['right'] , speed['slower']))
    rule29 = ctrl.Rule(distance['close'] & obstacle_deviation['farleft'] & deviation['right'], (steering['middle'] , speed['slower']))
    rule30 = ctrl.Rule(distance['close'] & obstacle_deviation['farleft'] & deviation['farright'], (steering['middle'] , speed['slower']))

    rule31 = ctrl.Rule(distance['close'] & obstacle_deviation['left'] & deviation['farleft'], (steering['right'] , speed['slower']))
    rule32 = ctrl.Rule(distance['close'] & obstacle_deviation['left'] & deviation['left'], (steering['right'] , speed['slower']))
    rule33 = ctrl.Rule(distance['close'] & obstacle_deviation['left'] & deviation['middle'], (steering['right'] , speed['slower']))
    rule34 = ctrl.Rule(distance['close'] & obstacle_deviation['left'] & deviation['right'], (steering['middle'] , speed['slower']))
    rule35 = ctrl.Rule(distance['close'] & obstacle_deviation['left'] & deviation['farright'], (steering['middle'] , speed['slower']))
 
    rule36 = ctrl.Rule(distance['close'] & obstacle_deviation['right'] & deviation['farleft'], (steering['middle'] , speed['slower']))
    rule37 = ctrl.Rule(distance['close'] & obstacle_deviation['right'] & deviation['left'], (steering['middle'] , speed['slower']))
    rule38 = ctrl.Rule(distance['close'] & obstacle_deviation['right'] & deviation['middle'], (steering['left'] , speed['slower']))
    rule39 = ctrl.Rule(distance['close'] & obstacle_deviation['right'] & deviation['right'], (steering['left'] , speed['slower']))
    rule40 = ctrl.Rule(distance['close'] & obstacle_deviation['right'] & deviation['farright'], (steering['left'] , speed['slower']))

    rule41 = ctrl.Rule(distance['close'] & obstacle_deviation['farright'] & deviation['farleft'], (steering['middle'] , speed['slower']))
    rule42 = ctrl.Rule(distance['close'] & obstacle_deviation['farright'] & deviation['left'], (steering['middle'] , speed['slower']))
    rule43 = ctrl.Rule(distance['close'] & obstacle_deviation['farright'] & deviation['middle'], (steering['left'] , speed['slower']))
    rule44 = ctrl.Rule(distance['close'] & obstacle_deviation['farright'] & deviation['right'], (steering['left'] , speed['slower']))
    rule45 = ctrl.Rule(distance['close'] & obstacle_deviation['farright'] & deviation['farright'], (steering['farleft'] , speed['slower']))

    rule46 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farleft'] & deviation['farleft'], (steering['farright'] , speed['stop']))
    rule47 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farleft'] & deviation['left'], (steering['farright'] , speed['stop']))
    rule48 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farleft'] & deviation['middle'], (steering['right'] , speed['slower']))
    rule49 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farleft'] & deviation['right'], (steering['middle'] , speed['slower']))
    rule50 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farleft'] & deviation['farright'], (steering['middle'] , speed['slower']))

    rule51 = ctrl.Rule(distance['very_close'] & obstacle_deviation['left'] & deviation['farleft'], (steering['farright'] , speed['stop']))
    rule52 = ctrl.Rule(distance['very_close'] & obstacle_deviation['left'] & deviation['left'], (steering['farright'] , speed['stop']))
    rule53 = ctrl.Rule(distance['very_close'] & obstacle_deviation['left'] & deviation['middle'], (steering['farright'] , speed['slower']))
    rule54 = ctrl.Rule(distance['very_close'] & obstacle_deviation['left'] & deviation['right'], (steering['farright'] , speed['slower']))
    rule55 = ctrl.Rule(distance['very_close'] & obstacle_deviation['left'] & deviation['farright'], (steering['middle'] , speed['slower']))
 
    rule56 = ctrl.Rule(distance['very_close'] & obstacle_deviation['right'] & deviation['farleft'], (steering['middle'] , speed['slower']))
    rule57 = ctrl.Rule(distance['very_close'] & obstacle_deviation['right'] & deviation['left'], (steering['left'] , speed['slower']))
    rule58 = ctrl.Rule(distance['very_close'] & obstacle_deviation['right'] & deviation['middle'], (steering['farleft'] , speed['slower']))
    rule59 = ctrl.Rule(distance['very_close'] & obstacle_deviation['right'] & deviation['right'], (steering['farleft'] , speed['stop']))
    rule60 = ctrl.Rule(distance['very_close'] & obstacle_deviation['right'] & deviation['farright'], (steering['farleft'] , speed['stop']))

    rule61 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farright'] & deviation['farleft'], (steering['middle'] , speed['slower']))
    rule62 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farright'] & deviation['left'], (steering['middle'] , speed['slower']))
    rule63 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farright'] & deviation['middle'], (steering['farleft'] , speed['slower']))
    rule64 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farright'] & deviation['right'], (steering['farleft'] , speed['stop']))
    rule65 = ctrl.Rule(distance['very_close'] & obstacle_deviation['farright'] & deviation['farright'], (steering['farleft'] , speed['stop']))
    
    obstacle_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5,
                                    rule6, rule7, rule8, rule9, rule10,
                                    rule11, rule12, rule13, rule14, rule15,
                                    rule16, rule17, rule18, rule19, rule20,
                                    rule21, rule22, rule23, rule24, rule25,
                                    rule26, rule27, rule28, rule29, rule30,
                                    rule31, rule32, rule33, rule34, rule35,
                                    rule36, rule37, rule38, rule39, rule40,
                                    rule41, rule42, rule43, rule44, rule45,
                                    rule46, rule47, rule48, rule49, rule50,
                                    rule51, rule52, rule53, rule54, rule55,
                                    rule56, rule57, rule58, rule59, rule65,
                                    rule61, rule62, rule63, rule64, rule65])
    obstacle_controller = ctrl.ControlSystemSimulation(obstacle_ctrl)
    return obstacle_controller
