Kytos have some events available, and to call them you should use the sintaxe
`this.$kytos.$emit()` passing as parameters the specific events names and its
objects of acceptance as documented bellow:

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

**k-status-bar**

============= ====== ================================== 
name          type   description                        
============= ====== ================================== 
statusMessage string Show a status message in StatusBar 
============= ====== ================================== 

