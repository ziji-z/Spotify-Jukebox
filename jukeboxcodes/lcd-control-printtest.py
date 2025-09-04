#import stuff for the lcd board
import time
'''import busio
import board
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd'''
import os

#os.chdir("/Users/zijizhou/Documents/Amherst/House/jukeboxcodes") #set directory
os.chdir(os.path.dirname(__file__))

#initilize all the lcd board stuff
# Modify this if you have a different sized Character LCD

'''lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)'''

current_text = ""
top_offset = 0 #for scrolling text top
bottom_offset = 0 #for scrolling text bottom

while True:
    lcd_file = open("lcd_output.txt","r+")
    lines = lcd_file.readlines()
    lcd_file.close()
    
    if int(lines[3]) < 10: #if we're displaying playlist, then lines 2 is the one we care about
        x = 2 #set the lines we're taking to 2
        
        #and the increment the time we wait
        f = open("lcd_output.txt","w")
        lines[3] = int(lines[3]) + 1
        f.write(lines[0]+lines[1]+lines[2]+str(lines[3]))
        # do the remaining operations on the file
        f.close()
    else: #if lines[3] is above what we want, then lines we take from to 1
        x = 1
        

    #fill in the blank spaces if the text is less then 16 chars
    if len(lines[0]) < 18:
        for i in range(18 - len(lines[0])):
            lines[0] = lines[0].split('\n')[0] + " " + "\n" 
    if len(lines[x]) < 18:
        for i in range(18 - len(lines[x])):
            lines[x] = lines[x].split('\n')[0] + " "
    
    current_text_new = lines[0] + lines[x]

    if current_text != current_text_new:
        temp = current_text.split('\n')
        current_text = current_text_new #if it's different, then set the current text to the new one

        #here to determine if we break up the offset or not
        if len(temp) >= 2:
            if temp[0] + "\n" != lines[0]: #if the top text changed
                top_offset = 0
            if temp[1] + "\n" != lines[x]:
                bottom_offset = 0
    
    if len(lines[0][:-1]) <= 16 and len(lines[x]) <= 16: #if both lines are contained by a single line, then we are chill and just print
        print(current_text) #set the message
    
    else: 
        if len(lines[0]) > 18: #the first line is too long
            topline = lines[0][top_offset:top_offset+16] + "\n"
            top_offset = top_offset + 1
            if top_offset + 16 > len(lines[0])-1: #if we've reached the end of the message
                top_offset = 0
        else: #first line is short enough
            topline = lines[0]
        
        if len(lines[x][:-1]) > 16: #the second line is too long
            bottomline = lines[x][bottom_offset:bottom_offset+16]
            bottom_offset = bottom_offset + 1
            if bottom_offset + 16 > len(lines[x][:-1]): #if we've reached the end of the message
                bottom_offset = 0
        else:
            bottomline = lines[x]
            
        print(topline + bottomline)
    
    
    time.sleep(0.5)