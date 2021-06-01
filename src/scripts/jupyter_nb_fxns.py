##### DEPRECATED ######
#from IPython.core.display import display, HTML
from IPython.display import display, HTML #for Jupyter Lab
#######################
###REQUIREMENTS:
# jupyter labextension install javascript-extension #install via commandline

from IPython.display import Javascript

toggle_code_str = '''
<form action="javascript:toggle_code()"><input type="submit" id="toggleButton" value="Unhide cell"></form>
'''

toggle_code_prepare_str = '''
    <script>
    function code_toggle() {
        if ($('div.cell.code_cell.rendered.selected div.input').css('display')!='none'){
            $('div.cell.code_cell.rendered.selected div.input').hide();
        } else {
            $('div.cell.code_cell.rendered.selected div.input').show();
        }
    }
    </script>

'''

display(HTML(toggle_code_prepare_str + toggle_code_str)) #DEPRECATED
#Javascript(toggle_code_prepare_str + toggle_code_str)

def toggle_code():
    display(HTML(toggle_code_str)) #DEPRECATED
    #Javascript(toggle_code_str)
