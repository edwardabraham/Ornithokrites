# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 18:05:56 2014

@author: Lukasz Tracewski

Reporting module
"""

import os
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import smtplib

class Reporter(object):
    
    def __init__(self, location, write_to_stdout):
        """
        Reporting results to the user
        
        Parameters
        ----------
        location : string
            Absolute or relative path
        write_to_stdout : bool
            Should the output be also directed to standard output
        """
        
        # First clean up
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)            
        # and create our logs
        self.Log = self._create_logger('log.html', location, write_to_stdout)
        self.DevLog = self._create_logger('devlog.html', location)      

    def _create_logger(self, name, path, stdout=False):
        if not os.path.exists(path):
            os.makedirs(path)
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(os.path.join(path, name),'w')
        formatter = logging.Formatter('%(message)s <br/>')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info('<!DOCTYPE html>')
        if stdout:
            logger.addHandler(logging.StreamHandler()) # for standard output (console)
        return logger

    def write_results(self, kiwi_result, individual_calls, filename, audio, rate, segmented_sounds):
        # sample_name_with_dir = filename.replace(os.path.split(os.path.dirname(filename))[0], '')[1:]              
        self.Log.info('%s: %s' % (filename.replace('/Recordings',''), kiwi_result))
        
        self.DevLog.info('<h2>%s</h2>' % kiwi_result)
        self.DevLog.info('<h2>%s</h2>' % filename.replace('/Recordings',''))
        self.DevLog.info('<audio controls><source src="%s" type="audio/wav"></audio>', 
                     filename.replace('/var/www/','').replace('/Recordings',''))    
        
        # Plot spectrogram
        plt.ioff()
        plt.specgram(audio, NFFT=2**11, Fs=rate)
        # and mark on it with vertical lines found audio features
        for i, (start, end) in enumerate(segmented_sounds):
            start /= rate
            end /= rate
            plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
            plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
            plt.text(start, 4000, i, fontsize=8)
            if individual_calls[i] == 1:
                plt.plot((start + end) / 2, 3500, 'go')
            elif individual_calls[i] == 2:
                plt.plot((start + end) / 2, 3500, 'bv')
        plt.axis('tight')
        title = plt.title(kiwi_result)
        title.set_y(1.03)
        spectrogram_sample_name = filename + '.png'
        plt.savefig(spectrogram_sample_name)
        plt.clf()
        path = spectrogram_sample_name.replace('/var/www/','').replace('/Recordings','')
        self.DevLog.info('<img src="%s" alt="Spectrogram">', path)
        self.DevLog.info('<hr>')
        
    def cleanup(self):
        self.Log.handlers = []
        self.DevLog.handlers = []
        logging.shutdown()
    
    def send_email(self):
        with open ("reporting.config", "r") as credentials:
            (gmail_user, gmail_pwd) = credentials.read().splitlines()
        FROM = 'Kiwi-Finder no-reply'
        TO = ['lukasz.tracewski@gmail.com'] #must be a list
        SUBJECT = "Kiwi-Finder: your data is ready"
        TEXT = """
               Kiwi-Finder.info has finished processing your recordings.
               Report is available here: http://kiwi-finder.info/results/log.html
               
               Cheers,
               http://kiwi-finder.info
               """
    
        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            #server = smtplib.SMTP(SERVER) 
            server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            #server.quit()
            server.close()
            print 'successfully sent the mail'
        except:
            print "failed to send mail"    
    