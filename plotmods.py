#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import _
from _ import p, d, MyObject, MyException
import natural_language_processing
import machine_learning_img
import myGame
import dialog_generator
import operate_sql
import twf

def PlotlyStream():
	# Make instance of stream id object 
	stream = plotly.graph_objs.Stream(
   		token=cfg["plotlyStreamToken"],  # (!) link stream id to 'token' key
		maxpoints=80      # (!) keep a max of 80 pts on screen
	)
	trace1 = plotly.graph_objs.Scatter(
		x=[],
		y=[],
		mode='lines+markers',
		stream = stream         # (!) embed stream id, 1 per trace
	)
	data = plotly.graph_objs.Data([trace1])
	# Add title to layout object
	layout = plotly.graph_objs.Layout(title='Time Series')
	
	# Make a figure object
	fig = plotly.graph_objs.Figure(data=data, layout=layout)
	
	# (@) Send fig to Plotly, initialize streaming plot, open new tab
	unique_url = plotly.plotly.plot(fig, filename='monitoring')
	print(unique_url)

def updateStream():
	s = plotly.plotly.Stream(cfg["plotlyStreamToken"])
	s.open()
	i = 0    # a counter
	k = 5    # some shape parameter
	N = 200  # number of points to be plotted
	
	# Delay start of stream by 5 sec (time to switch tabs)
	time.sleep(5)
	
	while True:
	    i += 1   # add to counter
	
	    # Current time on x-axis, random numbers on y-axis
	    x = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
	    y = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
	
	    # (-) Both x and y are numbers (i.e. not lists nor arrays)
	
	    # (@) write to Plotly stream!
	    s.write(dict(x=x, y=y))
	
	    # (!) Write numbers to stream to append current data on plot,
	    #     write lists to overwrite existing data on plot (more in 7.2).
	
	    time.sleep(0.1)  # (!) plot a point every 80 ms, for smoother plotting

	# (@) Close the stream when done plotting
	s.close()

if __name__ == '__main__':
	# plotly.plotly.Stream(cfg["plotlyStreamToken"]).close()
	PlotlyStream()
	updateStream()
