#!/usr/bin/env python
# coding=utf-8
"""
job_profiler.py - PBS hook that logs various metrics about a running job. As
the metrics gathering requires an idle system and can result in large logs,
a user must specifically request that his/her job be profiled. Once requested, 
the job is set to exclusive placement so that the metrics only apply to the
individual job itself.
"""

"""
Copyright (C) 1994-2017 Altair Engineering, Inc. All rights reserved.
For more information, contact Altair at www.altair.com.

This file is part of the PBS Professional ("PBS Pro") software.
    
Open Source License Information:

PBS Pro is free software. You can redistribute it and/or modify it under the
terms of the GNU Affero General Public License as published by the Free 
Software Foundation, either version 3 of the License, or (at your option) any 
later version.

PBS Pro is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along 
with this program.  If not, see <http://www.gnu.org/licenses/>.

Commercial License Information: 

The PBS Pro software is licensed under the terms of the GNU Affero General 
Public License agreement ("AGPL"), except where a separate commercial license 
agreement for PBS Pro version 14 or later has been executed in writing with Altair.

Altair's dual-license business model allows companies, individuals, and 
organizations to create proprietary derivative works of PBS Pro and distribute 
them - whether embedded or bundled with other software - under a commercial 
license agreement.

Use of Altair's trademarks, including but not limited to "PBS™", 
"PBS Professional®", and "PBS Pro™" and Altair's logos is subject to Altair's 
trademark licensing policies.

"""

import datetime

default_config={
        'receiver_port': 15103,
        'receiver_log': '/var/spool/PBS/profiler_logs/receiver.%s.log' % datetime.datetime.now().strftime('%Y%m%d'),
        'sender_log': '/var/spool/PBS/profiler_logs/sender.%s.log' % datetime.datetime.now().strftime('%Y%m%d'),
        'placement': 'excl',
        'metrics':  { 'load': {
                            'displayname': 'Load Average',
                            'cmd': r"""uptime | awk '{gsub(/,/,"");print $8}'"""},
                      'perc_mem': {
                            'displayname': 'Memory Used %',
                            'cmd': r"""free | awk '/Mem:/{total=$2}/cache:/{free=$4}END{printf "%1.2f\n",100-(total-free)/total*100}'"""},
                    },
        'httpd': True,
        'testhttpd': False
    }

class stub:
    """ Stub class for building subobjects """
    pass

def receiver(*kwargs):
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs
    from socket import gethostname, gethostbyaddr

    class Receiver(BaseHTTPRequestHandler):
        """
        Creates an http receiver
        """
        def __init__(self):
            self.html=stub()
            self.html.title='PBS Professional Job Profiler Receiver'
            self.html.body=''
            def _set_content_():
                return """<html><head><style>/*!
Pure v1.0.0
Copyright 2013 Yahoo!
Licensed under the BSD License.
https://github.com/yahoo/pure/blob/master/LICENSE.md
*/
/*!
normalize.css v^3.0 | MIT License | git.io/normalize
Copyright (c) Nicolas Gallagher and Jonathan Neal
*/
/*! normalize.css v3.0.3 | MIT License | github.com/necolas/normalize.css */img,legend{border:0}legend,td,th{padding:0}html{font-family:sans-serif;-ms-text-size-adjust:100%;-webkit-text-size-adjust:100%}self.html.body{margin:0}article,aside,details,figcaption,figure,footer,header,hgroup,main,menu,nav,section,summary{display:block}audio,canvas,progress,video{display:inline-block;vertical-align:baseline}audio:not([controls]){display:none;height:0}[hidden],template{display:none}a{background-color:transparent}a:active,a:hover{outline:0}abbr[title]{border-bottom:1px dotted}b,optgroup,strong{font-weight:700}dfn{font-style:italic}h1{font-size:2em;margin:.67em 0}mark{background:#ff0;color:#000}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sup{top:-.5em}sub{bottom:-.25em}svg:not(:root){overflow:hidden}figure{margin:1em 40px}hr{box-sizing:content-box;height:0}pre,textarea{overflow:auto}code,kbd,pre,samp{font-family:monospace,monospace;font-size:1em}button,input,optgroup,select,textarea{color:inherit;font:inherit;margin:0}button{overflow:visible}button,select{text-transform:none}button,html input[type=button],input[type=reset],input[type=submit]{-webkit-appearance:button;cursor:pointer}button[disabled],html input[disabled]{cursor:default}button::-moz-focus-inner,input::-moz-focus-inner{border:0;padding:0}input{line-height:normal}input[type=checkbox],input[type=radio]{box-sizing:border-box;padding:0}input[type=number]::-webkit-inner-spin-button,input[type=number]::-webkit-outer-spin-button{height:auto}input[type=search]{-webkit-appearance:textfield;box-sizing:content-box}input[type=search]::-webkit-search-cancel-button,input[type=search]::-webkit-search-decoration{-webkit-appearance:none}fieldset{border:1px solid silver;margin:0 2px;padding:.35em .625em .75em}table{border-collapse:collapse;border-spacing:0}.hidden,[hidden]{display:none!important}.pure-img{max-width:100%;height:auto;display:block}.pure-button{display:inline-block;zoom:1;line-height:normal;white-space:nowrap;vertical-align:middle;text-align:center;cursor:pointer;-webkit-user-drag:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;box-sizing:border-box}.pure-button::-moz-focus-inner{padding:0;border:0}.pure-button-group{letter-spacing:-.31em;text-rendering:optimizespeed}.opera-only :-o-prefocus,.pure-button-group{word-spacing:-.43em}.pure-button{font-family:inherit;font-size:100%;padding:.5em 1em;color:#444;color:rgba(0,0,0,.8);border:1px solid #999;border:transparent;background-color:#E6E6E6;text-decoration:none;border-radius:2px}.pure-button-hover,.pure-button:focus,.pure-button:hover{filter:alpha(opacity=90);background-image:-webkit-linear-gradient(transparent,rgba(0,0,0,.05) 40%,rgba(0,0,0,.1));background-image:linear-gradient(transparent,rgba(0,0,0,.05) 40%,rgba(0,0,0,.1))}.pure-button:focus{outline:0}.pure-button-active,.pure-button:active{box-shadow:0 0 0 1px rgba(0,0,0,.15) inset,0 0 6px rgba(0,0,0,.2) inset;border-color:#000\9}.pure-button-disabled,.pure-button-disabled:active,.pure-button-disabled:focus,.pure-button-disabled:hover,.pure-button[disabled]{border:none;background-image:none;filter:alpha(opacity=40);opacity:.4;cursor:not-allowed;box-shadow:none;pointer-events:none}.pure-button-hidden{display:none}.pure-button-primary,.pure-button-selected,a.pure-button-primary,a.pure-button-selected{background-color:#0078e7;color:#fff}.pure-button-group .pure-button{letter-spacing:normal;word-spacing:normal;vertical-align:top;text-rendering:auto;margin:0;border-radius:0;border-right:1px solid #111;border-right:1px solid rgba(0,0,0,.2)}.pure-button-group .pure-button:first-child{border-top-left-radius:2px;border-bottom-left-radius:2px}.pure-button-group .pure-button:last-child{border-top-right-radius:2px;border-bottom-right-radius:2px;border-right:none}.pure-form input[type=text],.pure-form input[type=number],.pure-form input[type=search],.pure-form input[type=tel],.pure-form input[type=color],.pure-form input[type=password],.pure-form input[type=email],.pure-form input[type=url],.pure-form input[type=date],.pure-form input[type=month],.pure-form input[type=time],.pure-form input[type=datetime],.pure-form input[type=datetime-local],.pure-form input[type=week],.pure-form select,.pure-form textarea{padding:.5em .6em;display:inline-block;border:1px solid #ccc;box-shadow:inset 0 1px 3px #ddd;border-radius:4px;vertical-align:middle;box-sizing:border-box}.pure-form input:not([type]){padding:.5em .6em;display:inline-block;border:1px solid #ccc;box-shadow:inset 0 1px 3px #ddd;border-radius:4px;box-sizing:border-box}.pure-form input[type=color]{padding:.2em .5em}.pure-form input:not([type]):focus,.pure-form input[type=text]:focus,.pure-form input[type=number]:focus,.pure-form input[type=search]:focus,.pure-form input[type=tel]:focus,.pure-form input[type=color]:focus,.pure-form input[type=password]:focus,.pure-form input[type=email]:focus,.pure-form input[type=url]:focus,.pure-form input[type=date]:focus,.pure-form input[type=month]:focus,.pure-form input[type=time]:focus,.pure-form input[type=datetime]:focus,.pure-form input[type=datetime-local]:focus,.pure-form input[type=week]:focus,.pure-form select:focus,.pure-form textarea:focus{outline:0;border-color:#129FEA}.pure-form input[type=file]:focus,.pure-form input[type=radio]:focus,.pure-form input[type=checkbox]:focus{outline:#129FEA auto 1px}.pure-form .pure-checkbox,.pure-form .pure-radio{margin:.5em 0;display:block}.pure-form input:not([type])[disabled],.pure-form input[type=text][disabled],.pure-form input[type=number][disabled],.pure-form input[type=search][disabled],.pure-form input[type=tel][disabled],.pure-form input[type=color][disabled],.pure-form input[type=password][disabled],.pure-form input[type=email][disabled],.pure-form input[type=url][disabled],.pure-form input[type=date][disabled],.pure-form input[type=month][disabled],.pure-form input[type=time][disabled],.pure-form input[type=datetime][disabled],.pure-form input[type=datetime-local][disabled],.pure-form input[type=week][disabled],.pure-form select[disabled],.pure-form textarea[disabled]{cursor:not-allowed;background-color:#eaeded;color:#cad2d3}.pure-form input[readonly],.pure-form select[readonly],.pure-form textarea[readonly]{background-color:#eee;color:#777;border-color:#ccc}.pure-form input:focus:invalid,.pure-form select:focus:invalid,.pure-form textarea:focus:invalid{color:#b94a48;border-color:#e9322d}.pure-form input[type=file]:focus:invalid:focus,.pure-form input[type=radio]:focus:invalid:focus,.pure-form input[type=checkbox]:focus:invalid:focus{outline-color:#e9322d}.pure-form select{height:2.25em;border:1px solid #ccc;background-color:#fff}.pure-form select[multiple]{height:auto}.pure-form label{margin:.5em 0 .2em}.pure-form fieldset{margin:0;padding:.35em 0 .75em;border:0}.pure-form legend{display:block;width:100%;padding:.3em 0;margin-bottom:.3em;color:#333;border-bottom:1px solid #e5e5e5}.pure-form-stacked input:not([type]),.pure-form-stacked input[type=text],.pure-form-stacked input[type=number],.pure-form-stacked input[type=search],.pure-form-stacked input[type=tel],.pure-form-stacked input[type=color],.pure-form-stacked input[type=file],.pure-form-stacked input[type=password],.pure-form-stacked input[type=email],.pure-form-stacked input[type=url],.pure-form-stacked input[type=date],.pure-form-stacked input[type=month],.pure-form-stacked input[type=time],.pure-form-stacked input[type=datetime],.pure-form-stacked input[type=datetime-local],.pure-form-stacked input[type=week],.pure-form-stacked label,.pure-form-stacked select,.pure-form-stacked textarea{display:block;margin:.25em 0}.pure-form-aligned .pure-help-inline,.pure-form-aligned input,.pure-form-aligned select,.pure-form-aligned textarea,.pure-form-message-inline{display:inline-block;vertical-align:middle}.pure-form-aligned textarea{vertical-align:top}.pure-form-aligned .pure-control-group{margin-bottom:.5em}.pure-form-aligned .pure-control-group label{text-align:right;display:inline-block;vertical-align:middle;width:10em;margin:0 1em 0 0}.pure-form-aligned .pure-controls{margin:1.5em 0 0 11em}.pure-form .pure-input-rounded,.pure-form input.pure-input-rounded{border-radius:2em;padding:.5em 1em}.pure-form .pure-group fieldset{margin-bottom:10px}.pure-form .pure-group input,.pure-form .pure-group textarea{display:block;padding:10px;margin:0 0 -1px;border-radius:0;position:relative;top:-1px}.pure-form .pure-group input:focus,.pure-form .pure-group textarea:focus{z-index:3}.pure-form .pure-group input:first-child,.pure-form .pure-group textarea:first-child{top:1px;border-radius:4px 4px 0 0;margin:0}.pure-form .pure-group input:first-child:last-child,.pure-form .pure-group textarea:first-child:last-child{top:1px;border-radius:4px;margin:0}.pure-form .pure-group input:last-child,.pure-form .pure-group textarea:last-child{top:-2px;border-radius:0 0 4px 4px;margin:0}.pure-form .pure-group button{margin:.35em 0}.pure-form .pure-input-1{width:100%}.pure-form .pure-input-3-4{width:75%}.pure-form .pure-input-2-3{width:66%}.pure-form .pure-input-1-2{width:50%}.pure-form .pure-input-1-3{width:33%}.pure-form .pure-input-1-4{width:25%}.pure-form .pure-help-inline,.pure-form-message-inline{display:inline-block;padding-left:.3em;color:#666;vertical-align:middle;font-size:.875em}.pure-form-message{display:block;color:#666;font-size:.875em}</style><title>%(title)s</title></head><body>%(body)s</body></html>""" % dict([(e,getattr(self.html,e)) for e in dir(self.html)])
            self.html.content=_set_content_

        def receiver_start(self,jobid):
            """
            Starts a receiver process for the job id specified
            Requires:
            <str> jobid: Job ID to associate the receiver logger
            Returns:
            { 'receiver': <port>@<exec_host> }
            """
            return {'receiver': self.address_string}

        def receiver_end(self,jobid):
            """
            Shuts down a receiver process for the job id specified
            Requires:
            <str> jobid: Job ID associated with the receiver logger
            Returns:
            { 'state': <int> }
            """
            return {'state': 0}

        def receiver_log(self,jobid,log_entry):
            """
            Logs output to a specific job's job_profiler.log
            Requires:
            <str> jobid: Job ID associated with the log entry
            <str> node: Node ID associated with the log entry
            Returns:
            { 'state': <int> }
            """
            return {'state': 0}

        def log_message(self, format, *args):
            """
            Overrides log_message to write to /var/spool/job_profiler_logs in
            receiver mode. testreceiver mode will write to stdout.
            """
            if options.receiver:
                import os
                if not os.path.exists(os.path.dirname(conf['receiver_log'])):
                    os.makedirs(os.path.dirname(conf['receiver_log']))
                open(conf['receiver_log'],'a').write("%s - - [%s] %s\n" %
                    (self.address_string(), self.log_date_time_string(), format%args))
            elif options.testreceiver:
                print "%s - - [%s] %s" % \
                    (self.address_string(), self.log_date_time_string(), format%args)

        def usage(self):
            """
            overrides GET request and sends appropriate data based on request
            """

            _usage_='<h2>%s</h2>' % self.html.title
            _usage_+='<h3>Receiver for the PBS Professional Job Profiler hook</h3>'
            for func in [f for f in dir(self) if f.startswith('receiver_')]:
                fd={'protocol': getattr(self, 'protocol', 'http'),
                    'server_name': self.server_name,
                    'listen_addr': self.listen_addr,
                    'func_name': func.replace('receiver_','')}
                for l in [s.strip() for s in func.__doc__.split('Requires:\n')[1].rsplit('Returns:\n')[0].strip().split('\n')]:
                    s=l.split(' ',2)
                    fd['attrs']={
                        'type': s[0].strip('<>'),
                        'name': s[1].rstrip(':'),
                        'desc': s[3] }
                _usage_+='<h4>%(protocol)s://%(listen_addr)s/%(func_name)s</h4>' % fd
                _usage_+='<pre>%s</pre>' % func.__doc__
                _usage_+='<form class="pure-form pure-form-aligned" id="%(func_name)s">' % fd
                for attr in fd['attrs']:
                    _usage_+='<div class="pure-control-group">'
                    _usage_+='<label for="%(name)s" title="%(desc)s">%(name)s</label>' % attr
                    _usage_+='<input id="%(name)s" name="%(name)s" type="text" required/>' % attr
                    _usage_+='</div>'
                _usage_+='<div class="pure-controls">'
                _usage_+='<button type="submit" class="pure-button pure-button-primary">Submit</button>'
                _usage_+='</div></form><br/>'
            _usage_+='<br/><i><b>DEBUG</b></i><br/>'
            _usage_+='<br/>'.join([
                '<b>CLIENT VALUES:</b>',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'GET_path=%s' % urlparse(self.path).path,
                'query=%s' % urlparse(self.path).query,
                'content-length=%s' % self.headers.getheader('content-length'),
                'POST_data=%s' % urlparse.parse_qs(self.rfile.read(int(self.headers.getheader('content-length')))),
                'request_version=%s' % self.request_version,
                '',
                '<b>SERVER VALUES:</b>',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                ])
            return _usage_

        def do_GET(self):
            """
            override the GET method
            """
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.html.body=usage()
            self.wfile.write(self.html.content())

        def do_POST(self):
            """
            override the POST method
            """
            content_length = int(self.headers.getheader('content-length'))
            args=urlparse.parse_qs(self.rfile.read(length))
            
            handler='receiver_' + urlparse(self.path).path.lstrip('/')
            
            if handler in dir(self):
                hf=getattr(self,handler)
                try:
                    print hf(args)
                except:
                    import sys
                    trace={
                        'line':      sys.exc_info()[2].tb_lineno,
                        'module':    sys.exc_info()[2].tb_frame.f_code.co_name,
                        'exception': sys.exc_info()[0].__name__,
                        'message':   sys.exc_info()[1].message,
                    }
                    print self.head
                    print """<h3>Exception %(exception) line %(line) in %(module)</h3>
                    <pre>%(message)s</pre>
                    </self.html.body></html>""" % trace

            else:
                usage()

    Protocol = "HTTP/1.0"

    # listen on all addresses at the specified port
    server_addr=(getattr(conf,'receiver_addr',''),getattr(conf,'receiver_port',''))

    self.server_name = gethostname() if not server_addr[0] else gethostbyaddr(server_addr[0])
    self.listen_addr = '%s:%s' % (self.server_name, server_addr[0])
    
    Reciever.protocol_version = Protocol
    httpd = HTTPServer(server_addr, Reciever)
    httpd.serve_forever()

def update_node_pickle(action,*kwargs):
    import os
    import cPickle as pickle

    if action == 'add' or action == 'update':
        update=True
    elif action == 'del':
        update=False
    else:
        raise ValueError("Unknown action %s." % action)

    if 'jobId' not in kwargs.keys():
        raise SyntaxError("jobId argument required")
    else:
        jobId=kwargs['jobId']

    receiver=None
    if 'receiver' in kwargs.keys():
        receiver=kwargs['receiver']

    node_pickle_f=os.path.join(pbs.pbs_conf['PBS_HOME'],'mom_priv','hooks','profiler.pickle')
    
    if os.path.exists(node_pickle):
        node_pickle=pickle.load(open(node_pickle_f, 'rb'))
    else:
        node_pickle={}

    if update:
        node_pickle[jobId]=receiver
    else:
        del node_pickle[jobId]

    pickle.dump(node_pickle, open(node_pickle_f, 'wb'))

def queuejob_handler():
    pass

def execjob_begin_handler():
    pass

def exechost_periodic_handler():
    pass

def execjob_end_handler():
    pass

def execjob_terminate_handler():
    execjob_end_handler()

in_hook=True
try:
    import pbs
except:
    in_hook=False

if in_hook:
    job=pbs.event().job

    if pbs.event().type == pbs.EXECHOST_PERIODIC:
        exechost_periodic_handler()

    elif 'PBS_JOB_PROFILE' not in job.Variable_List.keys() \
        or 'job_profile' not in job.Resource_List.keys():
        pbs.event().accept()

    if pbs.event().type == pbs.QUEUEJOB:
        queuejob_handler()
    elif pbs.event().type == pbs.EXECJOB_BEGIN:
        execjob_begin_handler()
    elif pbs.event().type == pbs.EXECJOB_END:
        execjob_end_handler()

else:
    import sys
    from optparse import OptionParser

    parser = OptionParser(version='%prog {0} - Copyright (c) 2016 Altair Engineering'.format(__version__))
    parser.add_option("-r", "--receiver", dest="receiver",
        help="Launch a profiler receiver")
    parser.add_option("-t", "--test-receiver", dest="testreceiver",
        help="Launch a test profiler receiver")
    (options, args) = parser.parse_args()

    if options.receiver or options.testreceiver:
        conf=get_config()
        reciever_port=conf['receiver_port'] if 'receiver_port' in conf else None
        ret=receiver(test=options.testreciever, port=receiver_port)
        sys.exit(ret)