import requests
import socket
import configparser


def the_hunter():
    # This will curl every IP in the subnet this machine is in to find the Octoprint Monitor API.
    # We are assuming this is a /24 subnet because, reasons.
    # Also assuming you mapped it to port 7070.

    # Get local IP
    #local_ip = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    local_ip = s.getsockname()[0]

    #Now we will split the IP by octet and build our calls.
    local_octet = local_ip.split('.')

    x = 1
    while x <= 255:

        base_ip = "{}.{}.{}.".format(local_octet[0], local_octet[1], local_octet[2])
        test_ip = "{}{}".format(base_ip, x)
        if test_ip != local_ip:
            base_url = 'http://{}:7070/find_me'.format(test_ip)
            try:
                print("Trying {}".format(test_ip))
                r = requests.get(base_url, timeout=.25)
                if r.status_code == 200:
                    if r.text == "FOUND ME!":
                        print("Found It")
                        config = configparser.ConfigParser()
                        config['op_monitor'] = {'ipaddress': test_ip}
                        with open('config.ini', 'w') as configfile:
                            config.write(configfile)
                        break
            except requests.exceptions.ConnectionError:
                pass
        x += 1



if __name__ == '__main__':
    the_hunter()