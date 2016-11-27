#!/usr/bin/python

# Test Python script to check Xbox controller events
# Requires lego-pi project from https://github.com/zephod/lego-pi
# See http://mattdyson.org/blog/2013/01/using-an-xbox-360-wireless-controller-with-raspberry-pi/
#
# Matt Dyson 05/01/2013
# http://mattdyson.org

import xbox_read

for event in xbox_read.event_stream(deadzone=12000):
	print event
