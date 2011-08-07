s=read.csv('accu2.csv')
attach(s)
postscript('volts.ps')
plot(min,volts,type='b')

postscript('amps.ps')
plot(min,amps,type='b')

postscript('mha.ps')
plot(min,mAh,type='b')
