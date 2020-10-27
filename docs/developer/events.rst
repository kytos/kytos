**k-action-menu**

================= ====== =========================================== 
name              type   description                                 
================= ====== =========================================== 
addActionMenuItem object Add a new action item in the k-action-menu. 
================= ====== =========================================== 

**k-info-panel**

============= ====== =========================================== 
name          type   description                                 
============= ====== =========================================== 
showInfoPanel Object Show the info panel in the right.           
hideInfoPanel NULL   Hide the info panel displayed in the right. 
============= ====== =========================================== 

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
