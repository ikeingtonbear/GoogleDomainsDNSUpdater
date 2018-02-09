#!/usr/bin/python3
import logging
import multiprocessing
import requests
import yaml

from time import sleep

class GoogleDomainsDNSUpdateDaemon(multiprocessing.Process):

    def __init__(self, configFile):
        multiprocessing.Process.__init__()
        self.daemon = True
        self.running = True
        self.ip = "0.0.0.0"
        self.readConfigFile(configFile)
        self.configureLogging()

    def configureLogging(self):
        """
        """
            #TODO Validate log path
            self.logger = logging.getLogger("gd2u")
            self.logger.setLevel(logging.DEBUG)
            logFormat = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
            logFile = logging.FileHandler(self.configs.get("global").get("log_path"))
            logFile.setLevel(logging.INFO)
            logFile.setFormatter(logFormat)
            self.logger.addHander(logFile)

            logStream = logging.StreamHandler()
            logStream.setLevel(logging.DEBUG)
            logStream.setFormatter(logFormat)
            self.logger.addHandler(logStream)

    def readConfigFile(self, file):
        """
        """
        #TODO Validate config path
        with open(file, 'r') as f:
            try:
                self.configs = yaml.load(f)
            except yaml.YAMLError as e:
                if hasattr(e, 'problem_mark'):
                    mark = e.problem_mark
                    print("Error parsing configuration file. Error position: ({0}, {1})".format(mark.line+1, mark.column+1))
                else:
                    print(e)
            #TODO Exit process/raise error since invalid configuration file

    def getIP(self):
        """
        """
        url = 'https://api.ipify.org'
        try:
            #TODO Validate valid IPv4 address?
            ip = requests.get(url).text
            return ip
        except:
            #TODO Handle exceptions from getting request
            self.logger.exception("Exception.")

    def ipChanged(self):
        """
        """
        curent_ip = self.getIP()
        if self.ip != current_ip:
            self.ip = current_ip
            self.logger.info("External IP changed. New IP: %s", self.ip)
            return True
        else:
            return False

    def updateRecord(self, domain, username, password):
        """
        """
        url = "https://{username}:{password}@domains.google.com/nic/update".format(username=username, password=password)
        data = {"hostname" : domain, "myip" : self.ip}

        try:
            r = requests.post(url, data=data)

            response = r.split()[1]
            if response == "good":
                self.logger.info("Record for %s updated to %s", domain, self.ip)
            elif response =="nochg":
                self.logger.info("Record for %s is already up-to-date", domain)
            elif response =="nohost":
                self.logger.warning("Record for %s does not exist, or does not have Dynamic DNS configured", domain)
            elif response =="badauth":
                self.logger.warning("The username/password combination is not valid for %s", domain)
            elif response =="notfqdn":
                self.logger.warning("%s is not a fully-qualified domain name", domain)
            elif response =="badagent":
                self.logger.critical("gd2ud is making bad requests")
                #TODO shutdown
            elif response =="abuse":
                self.logger.critical("gd2ud has been blocked for failure to interpret responses correctly")
                #TODO shutdown
            elif response =="911":
                self.logger.warning("Error occurred on Google's behalf")
                #TODO wait, try again? change wait time?
            else:
                self.logger.critical("Unknown respone '%s' from Google". response)

        except:
            #Handle exceptions
            self.logger.exception("Exception.")

    def run(self):
        """
        """
        self.logging.info("Starting gd2ud")

        while self.running:
            if self.ipChanged():
                for domain in self.configs.get('domains'):
                    self.updateRecord(domain.get('subdomain'), domain.get('username'), domain.get('password'))
            sleep(self.configs.get('global').get('update_interval'))

        self.logger.info("Stopping gd2ud")

if __name__ == "__main__":
    gd2ud = GoogleDomainsDNSUpdateDaemon("/opt/gd2u/gd2u.conf")
    gd2ud.start()
