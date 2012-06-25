import mako
from mako.lookup import TemplateLookup
from mako.exceptions import SyntaxException
import pprint

lookup = TemplateLookup(directories=[""],
                       )
render_template = lookup.get_template("test.mako")
data = "aaa"
print render_template.render()

print render_template.get_template("")
#print render_template.get_def("door").render()
#print render_template.get_def("window_color").render()
#pprint.pprint( render_template.__dict__)

