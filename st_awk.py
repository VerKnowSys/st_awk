# -*- coding: utf-8 -*-
import sublime, sublime_plugin
from subprocess import Popen, PIPE, STDOUT

class st_awkCommand(sublime_plugin.TextCommand):
    def run_command(self, edit, expr, inplace):
        """
        Actually run awk command
        """
        r = sublime.Region(0, self.view.size())
        content = self.view.substr(r)

        out = ''
        try:
            # Encode content to bytes for subprocess input
            content_bytes = content.encode('utf-8')
            p = Popen(['awk', expr], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            out_bytes, err_bytes = p.communicate(input=content_bytes)
            
            # Decode bytes back to strings
            out = out_bytes.decode('utf-8')
            err = err_bytes.decode('utf-8')
            
            if err != '':
                sublime.error_message('Error when run awk: \n' + err)
                return
        except OSError as e:
            sublime.error_message('''Error when run command awk: %s, errno: %d.\nawk is required on $PATH''' 
                % (e.strerror, e.errno))
            return
        except UnicodeDecodeError as e:
            sublime.error_message('Error decoding awk output. Output may contain non-UTF-8 characters.')
            return
        except UnicodeEncodeError as e:
            sublime.error_message('Error encoding document content. Document may contain non-UTF-8 characters.')
            return

        if inplace:
            self.view.replace(edit, sublime.Region(0, self.view.size()), out)
        else:
            new_view = self.view.window().new_file()
            new_view.insert(edit, 0, out)


    def run(self, edit, **args):
        """
        args: 
            'inplace' : if it's 'yes', replace current view with command result 
        """
        inplace = args['inplace'].lower() == 'yes'
        def onDone(expr):
            self.run_command(edit, expr, inplace)

        self.view.window().show_input_panel('Awk expression:', '', onDone, None, None)
        

# TODO in-line awk expr or .awk file
