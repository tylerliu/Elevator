import time
from tkinter import *

from Elevator import Elevator
from Scheduler import DynamicExpressScheduler, ExpressScheduler, MinMaxScheduler

canvas_width = 800
canvas_height = 600
elevator = None
cart_image = None
run_flag = True
master = None
floors = 7
schedule_list = {'Normal Scheduler': MinMaxScheduler, 'Express Scheduler': ExpressScheduler, 'Dynamic Express': DynamicExpressScheduler}
schedule_var = None
pressing_list = {'No pressing ▲': 'none', 'always pressing ▲': 'always', 'press ▲ when full': 'when_full'}
pressing_var = None
speed = 10
tick_remainder = 0

def tick():
    global speed, tick_remainder
    tick_remainder += speed
    while tick_remainder >= 1.0:
        canvas.delete("all")
        elevator.tick()
        canvas_draw()
        tick_remainder -= 1.0

def canvas_draw():
    pass
    draw_elevator()
    draw_queue()

def draw_elevator():

    # elevator shaft
    canvas.create_rectangle(50, 5, 0.15 * canvas_width+50, canvas_height,
                            outline='black', fill='grey', width=5)
    height_per_floor = (canvas_height - 5) / floors
    for i in range(1, floors):
        canvas.create_line(50, height_per_floor * i, 0.15 * canvas_width + 50, height_per_floor * i)
        canvas.create_text(25, height_per_floor * (i - 0.5), text=str(floors - i + 1),
                           font=("Purisa", 40), justify=CENTER)
    canvas.create_text(25, height_per_floor * (floors - 0.5), text='1',
                       font=("Purisa", 40), justify=CENTER)

    # elevator
    location = elevator.calc_location()
    location = location * elevator.step_from + (1 - location) * elevator.step_to
    location = floors - (location + 0.5)
    location = location * height_per_floor
    canvas.create_rectangle(50 + 10, location - 30,
                            0.15 * canvas_width + 50 - 10, location + 30,
                            outline='black', fill='white', width=3)

    for i in range(len(elevator.passengerLogger.passengers)):
        add_cart(50 + 10 + 5 + i * 45, location - 15)

def draw_queue():
    height_per_floor = (canvas_height - 5) / floors
    for i in range(1, floors):
        canvas.create_line(0.15 * canvas_width + 50, height_per_floor * i, 0.9 * canvas_width, height_per_floor * i)

    for f, wait_count in enumerate(elevator.queue.request_count()):

        loc = floors - (f + 0.5)
        loc = loc * height_per_floor

        indic_text = ("▲" if elevator.queue.up_request[f] else "") + "\n" + ("▼" if elevator.queue.down_request[f] else "")
        canvas.create_text(0.15 * canvas_width + 50 + 10 + 10, loc, text=indic_text,
                           font=("Purisa", 26), justify=CENTER, fill='green')

        for i in range(wait_count):
            if 0.15 * canvas_width + 50 + 10 + 20 + 50 * i > 0.8 * canvas_width:
                canvas.create_text(0.15 * canvas_width + 50 + 10 + 20 + 50 * i, loc, text='   ...',
                           font=("Purisa", 40), justify=LEFT)
                break
            add_cart(0.15 * canvas_width + 50 + 10 + 20 + 50 * i, loc - 15)
        if f != 0:
            canvas.create_text(0.95 * canvas_width, loc, text=str(wait_count) + "\nWait",
                               font=("Purisa", 26), justify=CENTER)
        else:
            canvas.create_text(0.6 * canvas_width, loc, text=str(elevator),
                               font=("Purisa", 26), justify=CENTER)

def add_cart(x, y):
    global cart_image
    if cart_image == None:
        cart_image = PhotoImage(file='cart.gif')
        cart_image = cart_image.subsample(6)

    canvas.create_image(x, y, image=cart_image, anchor=NW)

def window_event(event):
    pass

def window_event2():
    master.destroy()

def scheduler_change(*args):
    elevator.scheduler = schedule_list[schedule_var.get()]()

def pressing_change(*args):
    elevator.queue.pressing_up = pressing_list[pressing_var.get()]

def p_change(new_p):
    elevator.p = float(new_p) / 100.0 * (1/10)

def spped_change(new_speed):
    global speed
    speed = float(2.0 ** (int(new_speed) / 11)) - 1

def reset_elevator():
    global elevator
    p = elevator.p
    elevator = Elevator(scheduler=schedule_list[schedule_var.get()](),
                        floors=floors,
                        p=p, capacity=2, initial_count=0, pressing_up=pressing_list[pressing_var.get()])


if __name__ == '__main__':

    elevator = Elevator(scheduler=MinMaxScheduler(), floors=floors, p=1 / 20, capacity=2, initial_count=0)
    master = Tk()
    master.resizable = False
    master.title("Elevator")
    master.bind("<Configure>", window_event)
    master.protocol("WM_DELETE_WINDOW", window_event2)

    canvas = Canvas(master,
               width=canvas_width,
               height=canvas_height)
    canvas.pack(expand=YES, fill=BOTH)

    schedule_var = StringVar(master)
    pressing_var = StringVar(master)

    button0 = Button(master, text="Reset", fg='black',
                         command=reset_elevator)
    button0.pack(side=LEFT)

    button = OptionMenu(master, schedule_var, *schedule_list)
    button.config(width=20, font=('Helvetica', 12))
    schedule_var.set(next(iter(schedule_list)))
    schedule_var.trace("w", scheduler_change)
    button.pack(side=LEFT)

    button2 = OptionMenu(master, pressing_var, *pressing_list)
    button2.config(width=20, font=('Helvetica', 12))
    pressing_var.set(next(iter(pressing_list)))
    pressing_var.trace("w", pressing_change)
    button2.pack(side=LEFT)

    label1 = Label(master, text='  Load: ')
    label1.pack(side=LEFT)
    scale1 = Scale(master, from_=0, to_=100, orient=HORIZONTAL, length=150,
                   command=p_change)
    scale1.set(40)
    scale1.pack(side=LEFT, expand=True)
    label2 = Label(master, text='  Simulation Speed: ')
    label2.pack(side=LEFT)
    scale2 = Scale(master, from_=0, to_=100, orient=HORIZONTAL, length=150,
                   command=spped_change)
    scale2.pack(side=LEFT, expand=True)
    scale2.set(10)

    while run_flag:
        tick()
        master.update()
        time.sleep(0.01)
    master.destroy()