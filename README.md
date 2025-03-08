# EasyConfig

`EasyConfig` is a library for creating settings dialogs based on the PyQt library. It simplifies the process of creating and managing configuration dialogs, allowing developers to quickly generate interfaces for modifying application settings. With `EasyConfig`, you can focus on your application's functionality rather than the complexities of dialog creation.

## Installation

You can install `EasyConfig` using pip:

```bash
pip install easyconfig2
```

If you want to install the latest version from the repository, use:

```bash
git clone https://github.com/dantard/easyconfig2.git
cd easyconfig2
pip install .
```


## Philosophy

`EasyConfig` organizes configuration options in a tree structure. To use the library, create an `EasyConfig2` object and add the necessary configuration options to this tree.

A basic settings dialog can be created with the following code:

```python
config = EasyConfig2()
name = config.root().addString("name", pretty="Name", default="John Doe")
age = config.root().addInt("age", pretty="Age", default=30)
```

In this example:
- We first create an `EasyConfig2` object
- The `root()` method returns the root node of the configuration tree (an `EasyNode`)
- We add two configuration options: a string named "name" and an integer named "age"
- Each option has a key (first parameter), a display label (`pretty`), and a default value
- The methods return `EasyNode` objects that can be used to access or modify the values later

The key value (first parameter) serves two purposes:
1. It's used to access the value in your code
2. It becomes the key in the YAML file when configuration is saved

The `pretty` parameter defines the label shown in the dialog's user interface.

## Complete Example

Here's a complete example showing how to create and display a dialog:

```python
import sys
from PyQt5.QtWidgets import QApplication
from easyconfig2.easyconfig import EasyConfig2

app = QApplication(sys.argv)

config = EasyConfig2()
name = config.root().addString("name", pretty="Name", default="John Doe")
age = config.root().addInt("age", pretty="Age", default=30)

config.edit()
```

![Dialog example](images/img.png)

This creates a dialog with two options. Users can modify the values and press OK to close the dialog. The values are stored in the `config` object and can be accessed with the `get` method:

```python
name_value = name.get()  # Returns the current value of "name"
age_value = age.get()    # Returns the current value of "age"
``` 

You can also set values programmatically using the `set` method:

```python
name.set("Jane Doe")  # Changes the value of "name"
age.set(25)           # Changes the value of "age"
```

Changes made this way will be reflected in the dialog if it's still open.

## Saving and Loading Configuration

`EasyConfig` can save settings to YAML files and load them back:

```python
# Save current configuration to a file
config.save("config.yaml")

# Load configuration from a file
config.load("config.yaml")
```

**Important**: The `load()` method must be called after all options have been added to the configuration object. `EasyConfig` will only read values for options that were previously defined.

Here's a complete example demonstrating saving and loading:

```python
import sys
from PyQt5.QtWidgets import QApplication
from easyconfig2.easyconfig import EasyConfig2

app = QApplication(sys.argv)

# Create config object and add options
config = EasyConfig2()
name = config.root().addString("name", pretty="Name", default="John Doe")
age = config.root().addInt("age", pretty="Age", default=30)

# Load existing configuration (if any)
config.load("config.yaml")

# Show dialog and save if user presses OK
if config.edit():
    config.save("config.yaml")

print("Name:", name.get())
print("Age:", age.get())

sys.exit(app.exec_())
```

This will generate a YAML file like this:

```yaml
name: Jane Doe
age: 25
```

## Using Subsections

You can organize options into subsections that can be expanded or collapsed by the user. This helps manage complex configurations by grouping related options:

```python
config = EasyConfig2()
name = config.root().addString("name", pretty="Name", default="John Doe")
age = config.root().addInt("age", pretty="Age", default=30)

# Create an address subsection
section = config.root().addSubSection("address", pretty="Address")
city = section.addString("city", pretty="City", default="New York")
state = section.addString("state", pretty="State", default="NY")
```

This creates a dialog with a collapsible "Address" section:

![Dialog with subsection](images/img_1.png)

The corresponding YAML file will be structured hierarchically:

```yaml
name: Jane Doe
age: 88
address:
  city: New York
  state: NY
```

### Inheriting Properties

All parameters specified for a subsection are inherited by the options within it. For example, if the `hidden` parameter is set to `True` in a subsection, all options within that subsection will also be hidden:

```python
# Create a hidden section for private data
private_section = config.root().addSubSection("private_data", hidden=True)
ssn = private_section.addString("ssn", pretty="SSN", default="123-45-6789")
```

In this example, the `private_data` section and its `ssn` option won't appear in the dialog, but their values will still be saved in the YAML file and can be accessed programmatically.

## Available Node Types

The methods like `addString`, `addInt`, etc. are wrappers around a more general method called `add_child`. For example, `addString` is equivalent to:

```python
name = config.root().add_child(EasyInputBox("name", pretty="Name", default="John Doe"))
```

### Common Parameters

All `EasyNode` objects support these parameters:

- `key`: The identifier used to access the value and the key used in the YAML file
- `pretty`: The label shown in the dialog
- `default`: The default value
- `hidden`: If `True`, the option won't appear in the dialog but will be saved in the YAML
- `base64`: If `True`, the value will be saved as a base64-encoded string
- `immediate`: If `True`, signals will be emitted immediately when the value changes

### Node Types and Specific Parameters

#### Organization
- **Subsection** (`EasySubsection` via `addSubSection`): A collapsible section that can contain other options
  
#### Text and Numbers
- **Text Input** (`EasyInputBox` via `addString`): A string option that can be edited
  - `validator`: A `QValidator` object for input validation
  - `readonly`: If `True`, the user cannot change the value
  
- **Integer** (`EasyInt` via `addInt`): An integer value
  - `readonly`: If `True`, the user cannot change the value

- **Float** (`EasyFloat` via `addFloat`): A floating-point value
  - `readonly`: If `True`, the user cannot change the value

#### Selection
- **Checkbox** (`EasyCheckBox` via `addCheckBox`): A boolean option
- **Combobox** (`EasyComboBox` via `addComboBox`): A dropdown selection
  - `items`: List of strings for the dropdown options

#### Range Selection
- **Slider** (`EasySlider` via `addSlider`): Select a value within a range
  - `min`: Minimum value
  - `max`: Maximum value
  - `den`: Denominator for scaling (value will be divided by this)
  - `suffix`: String to display after the value
  - `show_value`: Whether to display the numeric value
  - `format`: Format string (e.g., "%.2f")
  - `align`: Alignment of the value display ("left", "right", or "center")

#### File Selection
- **File Dialog** (`EasyFileDialog` via `addFileChoice`, `addFolderChoice`): Select a file or folder
  - `extension`: File extension filter
  - `type`: Dialog type ("file" or "dir")

## Advanced Features

### Value Change Signals

Every node (except the root) can emit signals when its value changes. You can connect to these signals to perform actions when values are modified:

```python
# Connect to the value_changed signal
city.value_changed.connect(lambda n: print("City changed to", n.get()))
state.value_changed.connect(lambda n: print("State changed to", n.get()))
```

The `value_changed` signal is emitted when the value changes through the dialog interface. The signal provides the node object that emitted it, allowing you to access the new value with `get()`.

**Note**: If signals are connected before loading a configuration file, they will also be emitted during the loading process.

### Dependencies Between Options

`EasyConfig` supports creating dependencies between options. There are two types of dependencies:

1. **`EasyPairDependency`**: Enables or disables a node based on another node's value
2. **`EasyMandatoryDependency`**: Enables or disables the OK button based on a node's value

For example, to disable the address section if the age is 18 or less:

```python
config.add_dependency(EasyPairDependency(age, section, lambda x: x > 18))
```

This creates a dependency with three parameters:
- The controlling node (`age`)
- The dependent node (`section`)
- A function that determines when the dependent node should be enabled

To disable the OK button if the name field is empty:

```python
config.add_dependency(EasyMandatoryDependency(name, lambda x: x != ""))
```

This dependency takes two parameters:
- The node to check (`name`)
- A function that determines when the OK button should be enabled

### Complete Example with Dependencies

Here's a complete example demonstrating dependencies:

```python
import sys
from PyQt5.QtWidgets import QApplication
from easyconfig2.easyconfig import EasyConfig2
from easyconfig2.easydependency import EasyPairDependency, EasyMandatoryDependency


app = QApplication(sys.argv)

config = EasyConfig2()
name = config.root().addString("name", pretty="Name", default="John Doe")
age = config.root().addInt("age", pretty="Age", default=30)

section = config.root().addSubSection("address", pretty="Address")
city = section.addString("city", pretty="City", default="New York")
state = section.addString("state", pretty="State", default="NY")

# Disable the address section if the age is 18 or less
config.add_dependency(EasyPairDependency(age, section, lambda x: x > 18))

# Disable the OK button if the name is empty
config.add_dependency(EasyMandatoryDependency(name, lambda x: x != ""))

if config.edit():
    print("Name:", name.get())
    print("Age:", age.get())
    print("City:", city.get())
    print("State:", state.get())

sys.exit(app.exec_())
```