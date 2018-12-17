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
    os.system('mv upmpdcli.tmp /ro/etc/upmpdcli.conf')
    time.sleep(1)
    os.system('reboot')

@app.route('/save_credentials', methods = ['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']
    create_wpa_supplicant(ssid, wifi_key)
    os.system('mv wpa_supplicant.conf.tmp /ro/etc/wpa_supplicant/wpa_supplicant.conf')
    time.sleep(1)
    os.system('reboot')

@app.route('/dispon', methods = ['GET', 'POST'])
def dispon():
    os.system('systemctl start oled')
    return render_template('app.html')

@app.route('/dispoff', methods = ['GET', 'POST'])
def dispoff():
    os.system('systemctl stop oled')
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

@app.route('/squeeze', methods = ['GET', 'POST'])
def squeeze():
    os.system('mount -o remount rw /ro')
    os.system('cp /ro/etc/squeezelite /ro/etc/init.d')
    os.system('squeezelite -n GDis_squeeze -o hw:0 -z')
    os.system('cp /ro/root/overlayroot/templates/app_sq.html /ro/root/overlayroot/templates/app.html')
    os.system('cp /root/overlayroot/templates/app_sq.html /root/overlayroot/templates/app.html')
    os.system('mount -o remount ro /ro')
    return render_template('app.html')

@app.route('/upnp', methods = ['GET', 'POST'])
def upnp():
    os.system('mount -o remount rw /ro')
    os.system('killall squeezelite')
    os.system('rm /ro/etc/init.d/squeezelite')
    os.system('cp /ro/root/overlayroot/templates/app_up.html /ro/root/overlayroot/templates/app.html')
    os.system('cp /root/overlayroot/templates/app_up.html /root/overlayroot/templates/app.html')
    os.system('mount -o remount ro /ro')
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

    temp_conf_file = open('wpa_supplicant.conf.tmp', 'w')

    temp_conf_file.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    temp_conf_file.write('update_config=1\n')
    temp_conf_file.write('\n')
    temp_conf_file.write('network={\n')
    temp_conf_file.write('	ssid="' + ssid + '"\n')
    if wifi_key == '':
        temp_conf_file.write('	key_mgmt=NONE\n')
    else:
        temp_conf_file.write('	psk="' + wifi_key + '"\n')
    temp_conf_file.write('	}')
    temp_conf_file.close
    os.system('mount -o remount rw /ro')

def create_upmpdcli(ssid, wifi_key):

    temp_conf_file = open('upmpdcli.tmp', 'w')

    temp_conf_file.write('uprclautostart = 1\n')
    temp_conf_file.write('friendlyname = GDis-NP\n')
    temp_conf_file.write('msfriendlyname = GDis-Tidal-server\n')
    temp_conf_file.write('tidaluser = ' + ssid + '\n')
    temp_conf_file.write('tidalpass = ' + wifi_key + '\n')
    temp_conf_file.write('tidalquality = lossless\n')
    temp_conf_file.close
    os.system('mount -o remount rw /ro')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)
