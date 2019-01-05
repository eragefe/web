from flask import Flask, render_template, request
import subprocess
import os
import time

app = Flask(__name__)
app.debug = True


@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('app.html')

@app.route('/wifi')
def wifi():
    wifi_ap_array = scan_wifi_networks()

    return render_template('wifi.html', wifi_ap_array = wifi_ap_array)

@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')

@app.route('/tidal')
def tidal():
    return render_template('tidal.html')

@app.route('/tidal_save_credentials', methods = ['GET', 'POST'])
def tidal_save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']
    create_upmpdcli(ssid, wifi_key)
    os.system('mv upmpdcli.tmp /etc/upmpdcli.conf')
    time.sleep(1)
    os.system('reboot')

@app.route('/save_credentials', methods = ['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']
    create_wpa_supplicant(ssid, wifi_key)
    os.system('mv wifi.tmp /root/wifi')
    os.system('sed -i "$ i bash /root/wifi" /etc/rc.local')
    time.sleep(1)
    os.system('reboot')

@app.route('/dispon', methods = ['GET', 'POST'])
def dispon():
    os.system('python /root/neoplus2/oled2.py')
    return render_template('app.html')

@app.route('/dispoff', methods = ['GET', 'POST'])
def dispoff():
    pid = os.popen('pgrep -f oled').read().strip()
    os.system('kill -9 str(pid)')
    os.system('python /root/oled/off.py')
    return render_template('app.html')

@app.route('/reboot', methods = ['GET', 'POST'])
def reboot():
    time.sleep(1)
    os.system('reboot')

@app.route('/poweroff', methods = ['GET', 'POST'])
def poweroff():
    time.sleep(1)
    os.system('poweroff')

@app.route('/streamer', methods = ['GET', 'POST'])
def streamer():
    time.sleep(1)
    os.system('echo "0" > /sys/class/gpio/gpio198/value')
    os.system('echo "0" > /sys/class/gpio/gpio199/value')
    return render_template('app.html')

@app.route('/optical1', methods = ['GET', 'POST'])
def optical1():
    time.sleep(1)
    os.system('echo "1" > /sys/class/gpio/gpio198/value')
    os.system('echo "0" > /sys/class/gpio/gpio199/value')
    return render_template('app.html')

@app.route('/optical2', methods = ['GET', 'POST'])
def optical2():
    time.sleep(1)
    os.system('echo "1" > /sys/class/gpio/gpio198/value')
    os.system('echo "1" > /sys/class/gpio/gpio199/value')
    return render_template('app.html')

@app.route('/squeeze', methods = ['GET', 'POST'])
def squeeze():
    os.system('cp /etc/squeezelite /etc/init.d')
    os.system('squeezelite -n GDis_squeeze -o hw:0 -z')
    os.system('cp /root/neo2/templates/app_sq.html /root/neo2/templates/app.html')
    return render_template('app.html')

@app.route('/upnp', methods = ['GET', 'POST'])
def upnp():
    os.system('mount -o remount rw /media/root-ro')
    os.system('killall squeezelite')
    os.system('rm /media/root-ro/etc/init.d/squeezelite')
    os.system('cp /root/neo2/templates/app_up.html /root/neo2/templates/app.html')
    return render_template('app.html')

######## FUNCTIONS ##########

def scan_wifi_networks():
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array

def create_wpa_supplicant(ssid, wifi_key):

    temp_conf_file = open('wifi.tmp', 'w')

    temp_conf_file.write('nmcli r wifi on\n')
    temp_conf_file.write('nmcli d wifi connect ' + ssid + '  password  ' + wifi_key + '\n')
    temp_conf_file.close

def create_upmpdcli(ssid, wifi_key):

    temp_conf_file = open('upmpdcli.tmp', 'w')

    temp_conf_file.write('uprclautostart = 1\n')
    temp_conf_file.write('friendlyname = GDis-NP\n')
    temp_conf_file.write('msfriendlyname = GDis-Tidal-server\n')
    temp_conf_file.write('tidaluser = ' + ssid + '\n')
    temp_conf_file.write('tidalpass = ' + wifi_key + '\n')
    temp_conf_file.write('tidalquality = lossless\n')
    temp_conf_file.close

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)
