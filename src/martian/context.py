from martian.directive import UnknownError
from martian.util import scan_for_classes


class GetDefaultComponentFactory(object):

    def __init__(self, iface, component_name, directive_name):
        """Create a get_default_component function.

        iface - the iface that the component to be associated implements.
                for example: IContext
        component_name - the name of the type of thing we are looking for.
                for example: context
        directive_name - the name of the directive in use.
                for example: grok.context.
        """
        self.iface = iface
        self.component_name = component_name
        self.directive_name = directive_name

    def __call__(self, component, module, **data):
        """Determine module-level component.

        Look for components in module.

        iface determines the kind of module-level component to look for
        (it will implement iface).

        If there is no module-level component, raise an error.

        If there is one module-level component, it is returned.

        If there are more than one module-level component, raise
        an error.
        """
        components = list(scan_for_classes(module, self.iface))
        if len(components) == 0:
            raise UnknownError(
                "No module-level %s for %r, please use the '%s' "
                "directive."
                % (self.component_name, component, self.directive_name),
                component)
        elif len(components) == 1:
            return components[0]
        else:
            raise UnknownError(
                "Multiple possible %ss for %r, please use the '%s' "
                "directive."
                % (self.component_name, component, self.directive_name),
                component)
