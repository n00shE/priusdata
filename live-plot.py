import datetime
from panda import Panda
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

from panda_prius_dev import init_panda
p = init_panda()

def animate(i):
  speed_found = False
  while True:
    print('loop')
    can = p.can_recv()
    for address, _, dat, src  in can:
      if str(hex(address)) == '0xb4':
        print('found speed')
        speed_int = round((int(str(dat.hex())[-6:-2], 16) / 100) * 0.62137, 2)
        speed_found = True
        break
    if speed_found:
      break
  if speed_found:    
    now = datetime.datetime.now()
    dataDict[now.strftime("%S")] = speed_int
    xs = list(dataDict.keys())
    ys = list(dataDict.values())

    ax1.clear()
    ax1.set_ylabel('speed (mph)')
    ax1.set_xlabel('time (s)')
    ax1.set_title('Speed')
    ax1.plot(xs, ys)
    
    if len(dataDict.keys()) > 30:
        for k in dataDict:
            del dataDict[k]
            break

if __name__ == "__main__":
  dataDict = {}

  style.use('fivethirtyeight')
  fig = plt.figure()
  ax1 = fig.add_subplot(1,1,1)

  ani = animation.FuncAnimation(fig, animate, interval=1000)
  plt.show()