s=read.csv('accu2.csv')
attach(s)
pdf('accu2.pdf')
plot(min,volts,type='b')

plot(min,amps,type='b')

plot(min,mAh,type='b')
