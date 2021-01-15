import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import time, sys
from timeloop import Timeloop
from datetime import timedelta

'''
The main approch of this program includes these items
 1) Random number production    : function get_new_bid
 2) Decision-maker unit         : function get_new_bid
 3) Calculation part            : function do_deal
 4) Starting animated graphs    : draw_animated_graphs
 5) Updating graph data         : update_drawing
 6) Repeating items 1-3         : using wrapper function (job) of class Timeloop '''

#Define and initialize global variavles
my_animation = None

Deposit = 100000.0
buy_mean = 1005.0   #mean value of buy_bid random values
sell_mean = 995.0   #mean value of buy_bid random values
buy_std_dev = 20.0  #standard deviation value of buy bid random values
sell_std_dev = 20.0 #standard deviation value of  sell bid random values

buy_bid_array = []   # array to save buy bid random values
sell_bid_array = []  # array to save sell bid random values
bid_time_array = []  # array to save bid time values

sum_gain_array = [0.0]    # array to save aggregated gain values
deal_time_array = [0.0]   # array to save time values corresponding to gain values
deal_counter = 0          # conter for counting deals
calc_interval = 0.03     # interval between repeating each calculation step in seconds
anim_interval = 500     # interval for animation in miliseconds
#construct timeloop which provides a wrapper function to schecule and run functions in specified time intervals
my_time_loop = Timeloop()


fig = plt.figure(figsize=(9, 5))
fig.canvas.set_window_title('Online Investment Calculation Program')
gain_graph = fig.add_subplot(1, 2, 1)
buy_graph = fig.add_subplot(2, 2, 2)
sell_graph = fig.add_subplot(2, 2, 4)

fig.tight_layout(pad = 4)
gain_line, = gain_graph.plot([], [], 'b-', lw=1.4)
buy_line, = buy_graph.plot([], [], 'r-', lw =0.4)
sell_line, = sell_graph.plot([], [], 'b-', lw=0.4)

np.random.seed((3, 2))
start = time.time()

def init_graphs():
    gain_line.set_data([], [])
    gain_graph.set_title('Online Investment Gain')
    gain_graph.set_xlabel('Time')
    gain_graph.set_ylabel('Investment Gain')
    buy_line.set_data([], [])
    buy_graph.set_title('Buy Bid Graph')
    buy_graph.set_xlabel('Time')
    buy_graph.set_ylabel('Buy')
    sell_line.set_data([], [])
    sell_graph.set_title('Sell Bid Graph')
    sell_graph.set_xlabel('Time')
    sell_graph.set_ylabel('Sell')
    return gain_line, buy_line, sell_line,

   
def update_drawing(i):
    global deal_counter
    if deal_counter>0 :
        gain_line.set_data(deal_time_array, sum_gain_array)
        gain_graph.relim()
        gain_graph.autoscale_view(False, True, True)
        buy_line.set_data(bid_time_array, buy_bid_array)
        buy_graph.relim()
        buy_graph.autoscale_view(False, True, True)
        sell_line.set_data(bid_time_array, sell_bid_array)
        sell_graph.relim()
        sell_graph.autoscale_view(False, True, True)
    return gain_line, buy_line, sell_line,


def draw_animated_graphs():
    global my_animation
    #starting animated graphs, updating in specified intervals
    my_animation = animation.FuncAnimation(fig, update_drawing, init_func= init_graphs, \
                                           frames= None, interval= anim_interval, blit= False,    \
                                           repeat= False, cache_frame_data= False, save_count= None)
    #drawing three graphs
    plt.show()   
    print(len(buy_bid_array),len(sum_gain_array))
    #exit program when closing graph window
    sys.exit()
   

'''Decision_maker unit  1)repeating in specified intervals 2)producing random bids 
                        3)checking buy_bid and sell_bid and doing deal if condition satisfied
                        4)saving results in arrays to further use'''

# wraaper function 'job' of class 'Timeloop' repeats this function in the specified intervals
@my_time_loop.job(interval = timedelta(seconds = calc_interval))
def get_new_bid():
    global start, buy_mean, sell_mean, buy_std_dev, sell_std_dev
    buy_bid, sell_bid  = np.random.multivariate_normal([buy_mean, sell_mean], [[buy_std_dev, 0],[0, sell_std_dev]])
    if buy_bid < 0 or sell_bid < 0 : return  # ignores prices less than zero
    now = float(time.time() - start)
    buy_bid_array.append(buy_bid)
    sell_bid_array.append(sell_bid)
    bid_time_array.append(now)
    if buy_bid > sell_bid :
        do_deal(buy_bid, sell_bid, now)

#calculation and saving in arrays
def do_deal(buy, sell, now):
    global Deposit, deal_counter
    newstocks = int(Deposit / sell)
    expend = float(newstocks * sell)
    gain = float(newstocks * buy)
    difference = gain - expend
    if deal_counter > 1 :
        sum_gain_array.append(sum_gain_array[deal_counter-1] + difference)
        deal_time_array.append(now)
    elif deal_counter == 1 :
        sum_gain_array.append(difference)
        deal_time_array.append(now)
    Deposit += difference  
    deal_counter += 1




if __name__ == '__main__':
    #starting my_time_loop, which is an object of class Timeloop
    my_time_loop.start(block = False)
    #drawing animated graphs
    draw_animated_graphs()

    my_time_loop.stop()
   


