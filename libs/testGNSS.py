import proGNSS

gnss = proGNSS.GNSS()

while True:
    gnss.read()
    print(gnss.lat)
