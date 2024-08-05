import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

kivy.require('2.3.0')

# Class that allows text boxes to delete all values when clicked on
class ClearTextInput(TextInput):
    def on_focus(self, instance, value):
        if value:  # If the TextInput is focused set text to ''
            self.text = ''


# File that Deals with Form handling and Uploads
# TODO: Add Notion Integration, Add input Validation, Add getters and Setters
class FormFields(BoxLayout):

    # Init class; setup sizing and create fields
    def __init__(self, application_gui, num_fields: int, hint: float, **kwargs):
        
        # Box Layout Settings
        super(FormFields, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Set sizing; distribute fields equally in hieght
        self.size_hint_y = hint
        self.temp_y = 1 / num_fields

        # Create an array of all the ID Inputs and record the number of fields
        self.id_inputs = []
        self.num_fields = num_fields

        # Add form fields based off of the number of Fields 
        for _ in range(num_fields):
            self.__add_form_fields(application_gui)
            
    # Create and bind the form Fields so that they show up on the screen
    # TODO: Create events to handel state
    def __add_form_fields(self, application_gui):
        
        # Create new Layout that is horizontal
        form_layout = BoxLayout(size_hint_y=self.temp_y, size_hint_x=1)
        form_layout.orientation = 'horizontal'
        
        # Create new Id input and add it to list of inputs
        id_input = ClearTextInput(hint_text='ID', size_hint_y=1, multiline=False)
        id_input.bind(on_text_validate=self.on_enter)
        self.id_inputs.append(id_input)
        
        # Create Spinner object
        pass_fail_spinner = Spinner(text='Pass', values=['Pass', 'Fail'], size_hint_y=1)
        
        # Create Submit Button
        enter_button = Button(text='Enter', size_hint_y=1)
        enter_button.bind(on_press=lambda instance, id_input=id_input, pass_fail_spinner=pass_fail_spinner: self.__submit_form(instance, id_input, pass_fail_spinner))
        
        # Add Widgets to the Layout
        form_layout.add_widget(id_input)
        form_layout.add_widget(pass_fail_spinner)
        form_layout.add_widget(enter_button)
        
        # Add Layout to the UI
        self.add_widget(form_layout)

    # A function to define behavour when the enter key is pressed
    # NOTE: Do not go back to the top of the list or else it will refocus and delete top value
    def on_enter(self, instance):
        
        # Move focus to the next ID field only if there is another input
        current_index = self.id_inputs.index(instance)
        if current_index + 1 < len(self.id_inputs):
            self.id_inputs[current_index + 1].focus = True

    # A function handeling form submissions
    # TODO: Add notion integration
    def __submit_form(self, instance, id_input, pass_fail_spinner):
        id_value = id_input.text
        pass_fail_value = pass_fail_spinner.text
        #self.update_output_label(f'ID: {id_value}, Status: {pass_fail_value}')