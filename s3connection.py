# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 12:58:13 2014

@author: Lukasz Tracewski

Module for getting data from given S3 bucket.
"""

import os
import sys
import logging
import boto

def read_data(bucket_name='kiwicalldata', output_recordings_dir='./Recordings/'):
    """ 
    Downloads data from bucket to the specified directory.
    
    Parameters
    ----------
    bucket_name : string (default = 'kiwicalldata')
        Name of a S3 bucket to connect.
    output_recordings_dir : string (default = './Recordings/')
        Output directory where downloaded data will be stored. If directory
        does not exist it will be created recursively.
        
    Returns
    -------
    Nothing
    """
    log = logging.getLogger('log.html') 
    devlog = logging.getLogger('devlog.html') 
        
    try:
        log.info('Connecting to S3 ...')
        s3 = boto.connect_s3()
    except:
	logging.critical('Failure while connecting to S3. Check credentials.')
        sys.exit(1)
    try:
        log.info('Connection established. Fetching bucket %s...', bucket_name)
        bucket = s3.get_bucket(bucket_name)
    except:
        log.critical('Failure while connecting to bucket. Check if bucket exists.')
        sys.exit(1)    
    
    log.info('Bucket ready. Getting data ...')
    for key in bucket.list():
        if key.name.endswith('.wav') and not key.name.startswith('5mincounts'):
            devlog.info('Downloading %s', key.name)
            path = os.path.join(output_recordings_dir, key.name)
            _make_sure_dir_exists(path)
            key.get_contents_to_filename(path)
            
def _make_sure_dir_exists(filename):
    # Create recursively directory if it does not exist.
    dir_name = os.path.dirname(filename)
    if not os.path.exists( dir_name ):
        os.makedirs( dir_name )

""" Test """
if __name__ == '__main__':
    read_data()