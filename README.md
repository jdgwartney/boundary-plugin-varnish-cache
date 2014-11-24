Boundary Varnish Cache Plugin
=============================

The Boundary Varnish Cache plugin collects information on Varnish Cache.

The plugin requires the [varnishstat](https://www.varnish-cache.org/docs/4.0/reference/varnishstat.html#ref-varnishstat)
command to be available and in the system path.

The plugin requires Python 2.6 or later.

## Metrics

The information collected is a subset of what is returned by the
[varnishstat](https://www.varnish-cache.org/docs/4.0/reference/varnishstat.html#ref-varnishstat) command.

## Adding the Varnish Cache Plugin to Premium Boundary

1. Login into Boundary Premium
2. Display the settings dialog by clicking on the _settings icon_: ![](src/main/resources/settings_icon.png)
3. Click on the _Plugins_ in the settings dialog.
4. Locate the _varnish_cache_ plugin item and click on the _Install_ button.
5. A confirmation dialog is displayed indicating the plugin was installed successfully, along with the metrics and the dashboards.
6. Click on the _OK_ button to dismiss the dialog.

## Removing the Varnish Cache Plugin from Premium Boundary

1. Login into Boundary Premium
2. Display the settings dialog by clicking on the _settings icon_: ![](src/main/resources/settings_icon.png)
3. Click on the _Plugins_ in the settings dialog which lists the installed plugins.
4. Locate the _varnish_cache_ plugin and click on the item, which then displays the uninstall dialog.
5. Click on the _Uninstall_ button which displays a confirmation dialog along with the details on what metrics and dashboards will be removed.
6. Click on the _Uninstall_ button to perfom the actual uninstall and then click on the _Close_ button to dismiss the dialog.

## Configuration

The plugin will, by default, collect metrics from the Varnish instance named after the hostname of the machine it
is running on.  You can collect metrics on different instances by configuring one or more instance names.

General operations for plugins are described in [this article](http://premium-support.boundary.com/customer/portal/articles/1635550-plugins---how-to).
