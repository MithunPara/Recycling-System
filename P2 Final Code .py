import random
import time
import sys
sys.path.append('../')

from Common_Libraries.p2_sim_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()
update_thread = repeating_timer(2, update_sim)

## ***************************************************

def bin_location(container_ID): #identify autoclave bin function

    if (container_ID == 1): #red small container
        dropoff_location = [-0.62, 0.260, 0.362] #red small dropoff 
    elif (container_ID == 2): #green small container
        dropoff_location = [0.0, -0.681, 0.358] #green small dropoff
    elif (container_ID == 3): #blue small container
        dropoff_location = [0.0, 0.681, 0.358] #blue small dropoff 
    elif (container_ID == 4): #large red container
        dropoff_location = [-0.379, 0.2, 0.483] #large red dropoff 
    elif (container_ID == 5): #large green container
        dropoff_location = [0.0, -0.5, 0.5] #large green dropoff 
    elif (container_ID == 6): #large blue container
        dropoff_location = [0.0, 0.5, 0.5] #large blue dropoff 

    return dropoff_location  

 
def open_close_drawer(container_ID): #identify function to open/close autoclave drawers

    while True: #continue to loop until user input matches the sensor values
        if arm.emg_left() == 0 and arm.emg_right() > 0.5: 
            if (container_ID == 4):  #if container ID matches large red container
                arm.open_red_autoclave(True) #open red autoclave drawer
                break
            elif (container_ID == 5): #if container ID matches large green container
                arm.open_green_autoclave(True) #open green autoclave drawer
                break
            elif (container_ID == 6): #if container ID matches large blue container
                arm.open_blue_autoclave(True) #open blue autoclave drawer
                break 

                                 

def control_gripper(dropoff): #identify function to control gripper

    while True: 
        if arm.emg_left() > 0.5 and arm.emg_right() > 0.5:
            if dropoff == []:               #if coordinates for dropoff are not determined
                arm.control_gripper(45)     #gripper should close to pickup object
                break
            else:                           #if coordinates for dropoff are determined 
                arm.control_gripper(-45)    #open gripper to release object
                break
            

     


    
    
def move_coordinates(dropoff): #function to determine whether to move to pickup or dropoff location
    PICKUP = [0.517, 0.0, 0.031] #coordinates of pickup location
    
    if dropoff == []: #if the dropoff location has not been determined,
        return PICKUP #return pickup location
    else:
        return dropoff #if dropoff location is determined, return dropoff location


    
def move_end_effector(coordinates): 
    while True: 
        #depending on coordinates, move arm to pickup or dropoff location
        #is returned in previous function
        if arm.emg_left() > 0.5 and arm.emg_right() == 0:   
            arm.move_arm(coordinates[0],coordinates[1],coordinates[2]) 
            break 

 
 

def main(containers):  
        dropoff = [] #empty list for the dropoff location
        coordinates = [] #empty list to store dropoff or pickup coordinates

        arm.home() #moves Q-arm to home position
        time.sleep(3)

        container_ID = random.randint(1,6) #randomizes between all 6 containers
        
        while True: #keeps looping until new container number generates

            if container_ID in containers: #find random number again if an existing container is generated
                container_ID = random.randint(1,6)
            else:
                containers.append(container_ID) #add container number to end of list
                break
            
        arm.spawn_cage(container_ID) #spawns containers after each run through
        time.sleep(3) 
            
        coordinates = move_coordinates(dropoff) #gets the coordinates for pickup location
        move_end_effector(coordinates) #move to pick up location
        time.sleep(3)
        control_gripper(dropoff) #picks up object by closing gripper
        time.sleep(3)
        dropoff = bin_location(container_ID) #determine dropoff location depending on container ID
        coordinates = move_coordinates(dropoff) #get the dropoff location coordinates
        move_end_effector(coordinates) #move to dropoff location
        time.sleep(3)

        if 4 <= container_ID <= 6: #if object is large,
            open_close_drawer(container_ID) #open corresponding autoclave drawer
            time.sleep(2)

        control_gripper(dropoff) #releases object into autoclave
        time.sleep(3)

        #closes all of the autoclave drawers
        arm.open_red_autoclave(False)  
        arm.open_green_autoclave(False)  
        arm.open_blue_autoclave(False)

        time.sleep(3)

def loop():
    number_loops = 0 #keeps track of the containers placed
    containers = [] #holds container numbers to ensure different container

    while True:

        main(containers) #main function to pickup, dropoff, etc.
        number_loops += 1 #increment counter after container is placed

        if number_loops == 6: #after 6 containers have been placed, exit loop and return home
            arm.home()
            break


loop()



    




