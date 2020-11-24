Kytos has some events available, and to call them you should use the syntax
`this.$kytos.$emit()` passing as parameters the specific events names and its
objects of acceptance as documented below:

**k-action-menu**

================= ====== =========================================== 
name              type   description                                 
================= ====== =========================================== 
addActionMenuItem object Add a new action item in the k-action-menu. 
================= ====== =========================================== 

**Object Parameters:** The object should contain [name, author, shortkey, content]

**Example**

.. code-block:: html
    
    <template>
        ...
    </template>

    <script>
    /* All the javascript methods are optional */
    module.exports = {
        methods: {
            actionMethod()  {
                this.$kytos.$emit('statusMessage', 'Your Message Here')
            }
        },
        data() {
            return {
                options: {
                name: 'Status Bar Message Example', /* Name of the action */
                author: 'Kytos', /* Name of the author */
                shortkey: 'ctrl+alt+d', /* Shortkey to activate the action*/
                action: this.actionMethod /* Method to call as action */
                }
            }
        },
        mounted() {
            /* The event call */
            this.$kytos.$emit('addActionMenuItem', this.options)
        }
    }
    </script>

**k-info-panel**

============= ====== =========================================== 
name          type   description                                 
============= ====== =========================================== 
showInfoPanel Object Show the info panel in the right.           
hideInfoPanel NULL   Hide the info panel displayed in the right. 
============= ====== =========================================== 

The `k-info-panel` event can be triggered by a `k-button`, a
`k-action-menu` or anything that calls the method created to
set up a new `k-info-panel`.

**Example**

.. code-block:: html

    <template>
        ...
    </template>

    <script>
    /* All the javascript methods are optional */
    module.exports = {
        methods: {
            showInfoPanel()  {
                var content = {
                    "component": 'search-hosts',
                    "content": {msg:"content used in the component"},
                    "icon": "search",
                    "title": "Search Hosts",
                    "subtitle": "by kytos/UI Test"
                }
                this.$kytos.$emit("showInfoPanel", content)
                // this.$kytos.$emit("hideInfoPanel")
            }
        },
        data() {
            return {
            }
        }
    }
    </script>

**k-status-bar**

============= ====== ================================== 
name          type   description                        
============= ====== ================================== 
statusMessage string Show a status message in StatusBar 
============= ====== ================================== 
 
The example below uses the `mounted()` method that will display those messages
in the `k-status-bar` as soon the Kytos Web UI DOM is rendered.

**Example**

.. code-block:: html
    
    <template>
        ...
    </template>

    <script>
    /* All the javascript methods are optional */
    module.exports = {
        methods: { 
            // put your javascript methods here
        },
        mounted() {
            /* Will be displayed in kytos-blue */
            this.$kytos.$emit('statusMessage', 'Your Message Here')
            /* Will be displayed in kytos-red */
            this.$kytos.$emit('statusMessage', 'Your Message Here', true)
        }
    }
    </script>

**k-notification**

=============== ====== ===========================================================
name            type   description                        
=============== ====== =========================================================== 
setNotification object Define the icon, title and description of the notification 
=============== ====== =========================================================== 

To use the ``k-notification``, a notification object is necessary. Description
and icon are optional - the only required parameter is the tittle. Usage
example:

.. code-block:: html
    
    <template>
        ...
    </template>

    <script>
    /* All the javascript methods are optional */
    module.exports = {
        methods: { 
            // put your javascript methods here
        },
        mounted() {
            let notification = {
                title: 'Notification Title', 
                description: 'Notification Description', 
                icon: 'gear'
            }
            this.$kytos.$emit("Notification" , notification)
        }
    }
    </script>