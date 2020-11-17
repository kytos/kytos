=======================
Accordion | k-accordion
=======================


A GUI widget with a list of items (``k-accordion-item``) that can be switched between hiding and showing content.

**Image**

.. image:: /_static/images/components/accordion/k-accordion.png
    :align: center

**Example**

.. code-block:: shell

    <k-accordion>
        <k-accordion-item title="Custom Labels">
            <k-dropdown title="Switch Labels:" icon="circle-o" :options="switchLabels" :event="{name: 'topology-toggle-label', content: {node_type: 'switch'}}"></k-dropdown>
            <k-dropdown title="Interface Labels:" icon="plug" :options="interfaceLabels" :event="{name: 'topology-toggle-label', content: {node_type: 'interface'}}"></k-dropdown>
        </k-accordion-item>
        <k-accordion-item title="Background">
            <k-button-group>
                <k-button tooltip="Map Background" icon="globe"></k-button>
                <k-button tooltip="Image Background (disabled)" icon="photo" :is-disabled="true"></k-button>
                <k-button tooltip="No Background" icon="window-close-o"></k-button>
            </k-button-group>
            <k-slider icon="adjust" :initial-value="mapOpacity" :action="emitMapOpacity"></k-slider>
        </k-accordion-item>
    </k-accordion>

**Parameters**

========== ======= ======== ======= =================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= =================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
icon       string  false            An Icon string representing a awesome icon.                        
========== ======= ======== ======= =================================================================== 

**Methods**

**uuid4**: Return a uuid string

**Slots**

======= ===================================== 
name    description                           
======= ===================================== 
default Slot to be filled with accordion item 
======= ===================================== 

============================
Accordion | k-accordion-item
============================

A GUI widget that can be switched between hiding and showing content

**Example**

.. code-block:: shell

    <k-accordion>
        <k-accordion-item title="Background">
            <k-button-group>
                <k-button tooltip="Map Background" icon="globe"></k-button>
                <k-button tooltip="Image Background (disabled)" icon="photo" :is-disabled="true"></k-button>
                <k-button tooltip="No Background" icon="window-close-o"></k-button>
            </k-button-group>
            <k-slider icon="adjust" :initial-value="mapOpacity" :action="emitMapOpacity"></k-slider>
        </k-accordion-item>
    </k-accordion>

**Image**

.. image:: /_static/images/components/accordion/k-accordion-item.png
    :align: center

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
icon       string  false            An Icon string representing a awesome icon.                        
checked    boolean false    true    Boolean value to represent whether the accordion item is checked.  
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**Slots**

======= ============================================== 
name    description                                    
======= ============================================== 
default Empty Pannel, please define some items inside. 
======= ============================================== 

=================
Inputs | k-button
=================

This component represents a button that triggers an event when clicked.

**Example**

.. code-block:: shell

    <k-button tooltip="Request Circuit" title="Request Circuit" icon="gear" :action="request_circuit"></k-button>

**Image**

.. image:: /_static/images/components/input/k-button.png
    :align: center

**Parameters**

========== ======= ======== ========================= ================================================================== 
name       type    required default                   description                                                        
========== ======= ======== ========================= ================================================================== 
title      string  false                              Property representing a title                                      
tooltip    string  false                              Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false                     Property to represent show if the component is enabled ou disabled 
icon       string  false                              An Icon string representing a awesome icon.                        
on_click   func    false    function(val) { return; } Function called after the button is clicked.                       
========== ======= ======== ========================= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**click**: Call on_click event.

**Parameters**

===== ====== ============= 
name  type   description   
===== ====== ============= 
event object trigged event 
===== ====== ============= 

=======================
Inputs | k-button-group
=======================

Allows to group buttons (``k-button``), which trigger events when clicked.

**Example**

.. code-block:: shell

    <k-button-group>
        <k-button tooltip="Map Background" icon="globe"></k-button>
        <k-button tooltip="Image Background (disabled)" icon="photo" :is-disabled="true"></k-button>
        <k-button tooltip="No Background" icon="window-close-o"></k-button>
    </k-button-group>

**Image**

.. image:: /_static/images/components/input/k-button-group.png
    :align: center

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**Slots**

======= ==================================== 
name    description                          
======= ==================================== 
default Slot to be filled with a buttons set 
======= ==================================== 

===================
Inputs | k-checkbox
===================


A GUI widget that permits the user to make a binary choice, checked (ticked) when activated or not checked when disable.

**Image**

.. image:: /_static/images/components/input/k-checkbox.png
    :align: center

**Parameters**

========== ======= ======== =========================== ======================================================================================= 
name       type    required default                     description                                                                             
========== ======= ======== =========================== ======================================================================================= 
title      string  false                                Property representing a title                                                           
tooltip    string  false                                Defines a brief or informative message triggered by mouse hover                                                         
isDisabled boolean false    false                       Property to represent show if the component is enabled ou disabled                      
icon       string  false                                An Icon string representing a awesome icon.                                             
model      array   false                                Model store the checked values.                                                         
value      number  false    0                           The value to checkbox button.                                                           
checked    boolean false    false                       Initial value to checkbox, when true the checkbox will be checked, otherwise unchecked. 
action     func    false    function(value) { return; } Optinal action called after check a checkbox button.                                    
========== ======= ======== =========================== ======================================================================================= 

**Methods**

**uuid4**: Return a uuid string


===================
Inputs | k-dropdown
===================

A toggleable menu that allows the user to choose one value from a predefined list.

**Example**

.. code-block:: shell

    <k-dropdown title="Switch Labels:" icon="circle-o" :options="switchLabels" :event="{name: 'topology-toggle-label', content: {node_type: 'switch'}}"></k-dropdown>

**Image**

.. image:: /_static/images/components/input/k-dropdown.png
    :align: center

**Parameters**

========== ======= ======== =========================== ======================================================================= 
name       type    required default                     description                                                             
========== ======= ======== =========================== ======================================================================= 
title      string  false                                Property representing a title                                           
tooltip    string  false                                Defines a brief or informative message triggered by mouse hover                                         
isDisabled boolean false    false                       Property to represent show if the component is enabled ou disabled      
icon       string  false                                An Icon string representing a awesome icon.                             
value      string  false    ""                          Property with the selected option.                                      
options    array   true                                 A collection with all options that could be selected.                   
event      object  false                                An event triggered when the dropdown change, this event should have the 
                                                        following content: {**name**: 'event_name', **content**: {} }           
action     func    false    function(value) { return; } Optinal action called after select a dropdown option.                   
========== ======= ======== =========================== ======================================================================= 

**Methods**

**uuid4**: Return a uuid string

===================
Inputs | k-input
===================

An input field where the user can enter data.

**Image**

.. image:: /_static/images/components/input/k-input.png
    :align: center

**Parameters**

=========== ======= ======== ========================= ================================================================== 
name        type    required default                   description                                                        
=========== ======= ======== ========================= ================================================================== 
title       string  false                              Property representing a title                                      
tooltip     string  false                              Defines a brief or informative message triggered by mouse hover                                    
isDisabled  boolean false    false                     Property to represent show if the component is enabled ou disabled 
icon        string  false                              An Icon string representing a awesome icon.                        
value       string  false    ""                        The value to input button.                                         
placeholder string  false                              Placeholder string displayed in input field.                       
action      func    false    function(val) { return; } Function called after input changes.                               
=========== ======= ======== ========================= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

===================
Inputs | k-select
===================

This component is a form control and can be used to collect the selected user
input from a list of options.

**Example**

.. code-block:: shell

    <k-select icon="link" title="Undesired links:" :options="get_links" :value.sync ="undesired_links"></k-select>

**Image**

.. image:: /_static/images/components/input/k-select.png
    :align: center

**Parameters**

========== ======= ======== =========================== ================================================================== 
name       type    required default                     description                                                        
========== ======= ======== =========================== ================================================================== 
title      string  false                                Property representing a title                                      
tooltip    string  false                                Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false                       Property to represent show if the component is enabled ou disabled 
icon       string  false                                An Icon string representing a awesome icon.                        
value      array   false                                                                                                   
options    array   true                                                                                                    
event      object  false                                                                                                   
action     func    false    function(value) { return; }                                                                    
========== ======= ======== =========================== ================================================================== 

**Methods**

**uuid4**: Return a uuid string

=================
Inputs | k-slider
=================

A GUI widget that allows the users specify a numeric value which must be no less than a given value, and no more than another given value.

**Example**

.. code-block:: shell

    <k-slider icon="adjust" :initial-value="mapOpacity" :action="emitMapOpacity"></k-slider>

**Image**

.. image:: /_static/images/components/input/k-slider.png
    :align: center

**Parameters**

============ ======= ======== ========================= ================================================================== 
name         type    required default                   description                                                        
============ ======= ======== ========================= ================================================================== 
title        string  false                              Property representing a title                                      
tooltip      string  false                              Defines a brief or informative message triggered by mouse hover                                    
isDisabled   boolean false    false                     Property to represent show if the component is enabled ou disabled 
icon         string  false                              An Icon string representing a awesome icon.                        
initialValue number  false    0                         Initial value assigned to slider input.                            
action       func    false    function(val) { return; } Optinal action called after change the range of slider input.      
min          number  false    0                         Minimum value assigned to slider input.                            
max          number  false    100                       Maximum value assigned to slider input.                            
step         number  false    1                         The minimum change when the slider increase or decrease.           
============ ======= ======== ========================= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

===================
Inputs | k-textarea
===================

A text input field with multi-line.

**Parameters**

=========== ======= ======== =========================== ================================================================== 
name        type    required default                     description                                                        
=========== ======= ======== =========================== ================================================================== 
title       string  false                                Property representing a title                                      
tooltip     string  false                                Defines a brief or informative message triggered by mouse hover                               
isDisabled  boolean false    false                       Property to represent show if the component is enabled ou disabled 
icon        string  false                                An Icon string representing a awesome icon.                        
value       string  false                                The value text used in TextArea.                                   
modelValue  string  false    ""                                                                                             
placeholder string  false                                String displayed when the text-area is empty.                      
action      func    false    function(value) { return; } Optimal action called after textarea changes.                      
=========== ======= ======== =========================== ================================================================== 

**Methods**

**uuid4**: Return a uuid string

====================
Misc | k-action-menu
====================

Menu with a list of actions and their shortcuts. The menu can be shown or
hidden using the shortcut *Ctrl+Alt+Space*.

**Image**

.. image:: /_static/images/components/misc/k-action-menu.png
    :align: center

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
icon       string  false            An Icon string representing a awesome icon.                        
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**add_action_menu_item**: Method to add new action menu item

**Parameters**

======= ====== =========================================================== 
name    type   description                                                 
======= ====== =========================================================== 
options object An object with the params [name, author, shortkey, content] 
======= ====== =========================================================== 

======================
Misc | k-context-panel
======================

Represents a context where the developer can add any desired content.

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                   
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
icon       string  false            An Icon string representing a awesome icon.                        
subtitle   string  false                                                                               
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**Slots**

======= ==================================== 
name    description                          
======= ==================================== 
default Can be filled with the panel content 
======= ==================================== 

===================
Misc | k-info-panel
===================

Shows details about selected kytos components. This panel appears on the
right of the Kytos GUI and the NApp developer can choose what to display on
the panel.

**Image**

.. image:: /_static/images/components/misc/k-info-panel.png
    :align: center

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
icon       string  false            An Icon string representing a awesome icon.                        
subtitle   string  false                                                                               
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**show**: Show the Info Panel displayed in the right.

**Parameters**

======= ====== ======================================================= 
name    type   description                                             
======= ====== ======================================================= 
content object An object filled with:                                  
                                                                       
               {                                                       
               **component**: "search-hosts",                          
               **content**: {**msg**:"content used in the component"}, 
               **title**: "Search Hosts",                              
               **icon**: "desktop"                                     
               }                                                       
======= ====== ======================================================= 

=================
Misc | k-menu-bar
=================

A base components with icon in property.

**Parameters**

========== ========= ======== ======= ================================================================== 
name       type      required default description                                                        
========== ========= ======== ======= ================================================================== 
title      string    false            Property representing a title                                      
tooltip    string    false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean   false    false   Property to represent show if the component is enabled ou disabled 
icon       string    false            An Icon string representing a awesome icon.                        
toggle     undefined false                                                                               
compacted  undefined false                                                                               
========== ========= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

===================
Misc | k-status-bar
===================

A GUI widget the shows notifications and System Information.

**Image**

.. image:: /_static/images/components/misc/k-status-bar.png
    :align: center

**Methods**

**set_status**: Display a message inside the k-status-bar.

**Parameters**

======= ======= ========================================================= 
name    type    description                                               
======= ======= ========================================================= 
message string  Message to be displayed.                                  
error   boolean If true will display the message in red, default is false 
======= ======= ========================================================= 

=====================
Misc | k-toolbar-item
=====================

Component representing a toolbar item that create a new item in the
``k-menu-bar`` and shows the content in the ``k-toolbar``.

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
icon       string  false            An Icon string representing a awesome icon.                        
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**Slots**

======= =========================== 
name    description                 
======= =========================== 
default Slot with the toolbar item. 
======= =========================== 

=========================
ppanel | k-property-panel
=========================

This component allows to create a table with two columns ( *name* and *value*). Each row in the table is a ``k-property-panel-item`` component, with the *value* and *name*.

**Image**

.. image:: /_static/images/components/ppanel/k-property-panel.png
    :align: center

**Example**

.. code-block:: shell

    <k-property-panel>
        <k-property-panel-item v-if="napps"
                            v-for="napp in this.napps"
                            :key="napp.name"
                            :name="napp.name"
                            :value="napp.version">
        </k-property-panel-item>
    </k-property-panel>

**Parameters**

========== ======= ======== ======= ================================================================== 
name       type    required default description                                                        
========== ======= ======== ======= ================================================================== 
title      string  false            Property representing a title                                      
tooltip    string  false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false   Property to represent show if the component is enabled ou disabled 
========== ======= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

**Slots**

======= =============================================================== 
name    description                                                     
======= =============================================================== 
default Define a table content inside, a PropertyPanelItem can be used. 
======= =============================================================== 

==============================
ppanel | k-property-panel-item
==============================

This component create a row in the table (``k-property-panel``) with two columns, *name* and *value*.

**Image**

.. image:: /_static/images/components/ppanel/k-property-panel-item.png
    :align: center

**Example**

.. code-block:: shell

    <k-property-panel>
        <k-property-panel-item :name="kytos/mef_eline"
                            :value="2.2.0
        </k-property-panel-item>
    </k-property-panel>

**Parameters**

========== ============= ======== ======= ================================================================== 
name       type          required default description                                                        
========== ============= ======== ======= ================================================================== 
title      string        false            Property representing a title                                      
tooltip    string        false            Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean       false    false   Property to represent show if the component is enabled ou disabled 
name       string        true             Name displayed in the header of property panel item.               
value      string|number true             Value displayed in the data of property panel item.                
========== ============= ======== ======= ================================================================== 

**Methods**

**uuid4**: Return a uuid string

===============
table | k-table
===============

This component allows to create a table.

**Parameters**

========== ======= ======== ========================= ================================================================== 
name       type    required default                   description                                                        
========== ======= ======== ========================= ================================================================== 
title      string  false                              Property representing a title                                      
tooltip    string  false                              Defines a brief or informative message triggered by mouse hover                                    
isDisabled boolean false    false                     Property to represent show if the component is enabled ou disabled 
headers    array   false    function() { return []; }                                                                    
rows       array   false    function() { return []; }                                                                    
========== ======= ======== ========================= ================================================================== 

**Methods**

**uuid4**: Return a uuid string
