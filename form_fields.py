import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
#from custom_text_input import ClearTextInput

kivy.require('2.0.0')

class ClearTextInput(TextInput):
    def on_focus(self, instance, value):
        if value:  # If the TextInput is focused
            self.text = ''


# File that Deals with Form handling and Uploads
# TODO: Add Notion Integration, Add input Validation, Add getters and Setters
class FormFields(BoxLayout):

    def __init__(self, application_gui, num_fields: int, **kwargs):
        super(FormFields, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 160  # Adjust height based on the number of form fields

        self.id_inputs = []

        for _ in range(num_fields + 1):
            self.__add_form_fields(application_gui)
            
    # Create and bind the form Fields so that they show up on the screen
    # TODO: Create events to handel state
    def __add_form_fields(self, application_gui):
            form_layout = BoxLayout(size_hint_y=None, height=40)
            id_input = ClearTextInput(hint_text='ID', size_hint_y=None, height=40, multiline=False)
            id_input.bind(on_text_validate=self.on_enter)
            id_input.bind(on_focus=self.__on_focus)  # Bind the on_focus event
            self.id_inputs.append(id_input)
            pass_fail_spinner = Spinner(
                text='Pass',
                values=['Pass', 'Fail'],
                size_hint_y=None,
                height=40
            )
            enter_button = Button(text='Enter', size_hint_y=None, height=40)
            enter_button.bind(on_press=lambda instance, id_input=id_input, pass_fail_spinner=pass_fail_spinner: self.__submit_form(instance, id_input, pass_fail_spinner))
            form_layout.add_widget(id_input)
            form_layout.add_widget(pass_fail_spinner)
            form_layout.add_widget(enter_button)
            self.add_widget(form_layout)

    # A function to define behavour when the enter key is pressed
    def on_enter(self, instance):
        # Move focus to the next ID field
        current_index = self.id_inputs.index(instance)
        if current_index + 1 < len(self.id_inputs):
            self.id_inputs[current_index + 1].focus = True

    # When the text area is focused, Deleted all text in it
    def __on_focus(self, instance, value):
        if value:  # If the TextInput is focused
            instance.text = ''

    # A function handeling form submissions
    # TODO: Add notion integration
    def __submit_form(self, instance, id_input, pass_fail_spinner):
        id_value = id_input.text
        pass_fail_value = pass_fail_spinner.text
        #self.update_output_label(f'ID: {id_value}, Status: {pass_fail_value}')