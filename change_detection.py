from __future__ import division
from __future__ import print_function

import os
import sys
import errno

import math
import random
import itertools

import numpy as np
import psychopy

import templateexperiments as template

# Things you probably want to change
number_of_trials_per_block = 10
number_of_blocks = 2
percent_same = .5  # between 0 and 1
set_sizes = [6]
stim_size = 1.5  # visual degrees, used for X and Y

single_probe = True  # False to display all stimuli at test
repeat_stim_colors = False  # False to make all stimuli colors unique
repeat_test_colors = False  # False to make test colors unique from stim colors

keys = ['s', 'd']  # first is same
distance_to_monitor = 90

instruct_text = [
    ('Welcome to the experiment. Press space to begin.'),
    ('In this experiment you will be remembering colors.\n\n'
     'Each trial will start with a fixation cross. '
     'Do your best to keep your eyes on it.\n\n'
     'Then, 6 squares with different colors will appear. '
     'Remember as many colors as you can.\n\n'
     'After a short delay, the squares will reappear.\n\n'
     'If they all have the SAME color, press the "S" key. '
     'If any of the colors are DIFFERENT, press the "D" key.\n'
     'If you are not sure, just take your best guess.\n\n'
     'You will get breaks in between blocks.\n\n'
     'Press space to start.'),
]

data_directory = os.path.join(
    os.path.expanduser('~'), 'Desktop', 'ChangeDetection', 'Data')

# Things you probably don't need to change, but can if you want to
exp_name = 'ChangeDetection'

iti_time = 1
sample_time = .25
delay_time = 1

allowed_deg_from_fix = 15

# minimum euclidean distance of stimuli in precent of allowed space
min_distance = 0.1
max_per_quad = 2  # int or None for totally random displays

colors = [
    [ 1, -1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1,  1, -1],
    [ 1, -1,  1],
    [-1,  1,  1],
    [ 1,  1,  1],
    [-1, -1, -1],
    [ 1,  0, -1],
]

data_fields = [
    'Block',
    'Trial',
    'Timestamp',
    'Condition',
    'SetSize',
    'RT',
    'CRESP',
    'RESP',
    'ACC',
    'LocationTested',
    'Locations',
    'SampleColors',
    'TestColors',
]

gender_options = [
    'Male',
    'Female',
    'Other/Choose Not To Respond',
]

hispanic_options = [
    'Yes, Hispanic or Latino/a',
    'No, not Hispanic or Latino/a',
    'Choose Not To Respond',
]

race_options = [
    'American Indian or Alaskan Native',
    'Asian',
    'Pacific Islander',
    'Black or African American',
    'White / Caucasian',
    'More Than One Race',
    'Choose Not To Respond',
]

# Add additional questions here
questionaire_dict = {
    'Age': 0,
    'Gender': gender_options,
    'Hispanic:': hispanic_options,
    'Race': race_options,
}


# This is the logic that runs the experiment
# Change anything below this comment at your own risk
class Ktask(template.BaseExperiment):
    """
    """

    def __init__(self, number_of_trials_per_block=number_of_trials_per_block,
                 number_of_blocks=number_of_blocks, percent_same=percent_same,
                 set_sizes=set_sizes, stim_size=stim_size, colors=colors,
                 keys=keys, allowed_deg_from_fix=allowed_deg_from_fix,
                 min_distance=min_distance, max_per_quad=max_per_quad,
                 instruct_text=instruct_text, single_probe=single_probe,
                 iti_time=iti_time, sample_time=sample_time,
                 delay_time=delay_time, repeat_stim_colors=repeat_stim_colors,
                 repeat_test_colors=repeat_test_colors, **kwargs):

        self.number_of_trials_per_block = number_of_trials_per_block
        self.number_of_blocks = number_of_blocks
        self.percent_same = percent_same
        self.set_sizes = set_sizes
        self.stim_size = stim_size

        self.colors = colors

        self.iti_time = iti_time
        self.sample_time = sample_time
        self.delay_time = delay_time

        self.keys = keys

        self.allowed_deg_from_fix = allowed_deg_from_fix

        self.min_distance = min_distance

        if max_per_quad is not None and max(self.set_sizes)/4 > max_per_quad:
            raise ValueError('Max per quad is too small.')

        self.max_per_quad = max_per_quad

        self.instruct_text = instruct_text

        self.single_probe = single_probe
        self.repeat_stim_colors = repeat_stim_colors
        self.repeat_test_colors = repeat_test_colors

        self.same_trials_per_set_size = int((
            number_of_trials_per_block / len(set_sizes)) * percent_same)

        if self.same_trials_per_set_size % 1 != 0:
            raise ValueError('Each condition needs a whole number of trials.')
        else:
            self.diff_trials_per_set_size = (
                number_of_trials_per_block - self.same_trials_per_set_size)

        super(Ktask, self).__init__(**kwargs)

    @staticmethod
    def chdir():
        try:
            os.makedirs(data_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        os.chdir(data_directory)

    def make_block(self):
        trial_list = []

        self.same_trials_per_set_size

        for set_size in self.set_sizes:
            for _ in range(self.same_trials_per_set_size):
                trial = self.make_trial(set_size, 'same')
                trial_list.append(trial)

            for _ in range(self.diff_trials_per_set_size):
                trial = self.make_trial(set_size, 'diff')
                trial_list.append(trial)

        random.shuffle(trial_list)

        return trial_list

    def make_trial(self, set_size, condition):
        if condition == 'same':
            cresp = self.keys[0]
        else:
            cresp = self.keys[1]

        test_location = random.choice(range(set_size))

        if self.repeat_stim_colors:
            stim_colors = [random.choice(self.colors) for _ in range(set_size)]
        else:
            stim_colors = random.sample(self.colors, set_size)

        if self.repeat_test_colors:
            test_color = random.choice(self.colors)
            while test_color == self.colors[test_location]:
                test_color = random.choice(self.colors)
        else:
            test_color = random.choice(
                [color for color in self.colors if color not in stim_colors])

        if self.max_per_quad is not None:
            # quad boundries (x1, x2, y1, y2)
            quad_count = [0, 0, 0, 0]

        grid_dist = self.min_distance * 2
        grid_jitter = random.uniform(0, grid_dist)
        num_lines = int(math.floor(1 / (grid_dist)))
        center = np.array([.5, .5])
        grid = []
        for x in range(num_lines):
            for y in range(num_lines):
                loc = [(grid_dist * x) + grid_jitter,
                       (grid_dist * y) + grid_jitter]

                dist_to_center = np.linalg.norm(np.array(loc) - center)
                too_big = loc[0] >= 1 or loc[1] >= 1

                # Add it if it's not too close to the center or outside range
                if not dist_to_center < grid_dist and not too_big:
                    grid.append(loc)

        locs = []
        while len(locs) <= set_size:
            grid_attempt = random.choice(grid)
            attempt = [coord + random.uniform(-self.min_distance / 2,
                                              self.min_distance / 2)
                       for coord in grid_attempt]

            if self.max_per_quad is not None:
                if attempt[0] < 0.5 and attempt[1] < 0.5:
                    quad = 0
                elif attempt[0] >= 0.5 and attempt[1] < 0.5:
                    quad = 1
                elif attempt[0] < 0.5 and attempt[1] >= 0.5:
                    quad = 2
                else:
                    quad = 3

                if quad_count[quad] < self.max_per_quad:
                    quad_count[quad] += 1
                    grid.remove(grid_attempt)
                    locs.append(attempt)
            else:
                grid.remove(grid_attempt)
                locs.append(attempt)

        trial = {
            'set_size': set_size,
            'condition': condition,
            'cresp': cresp,
            'locations': locs,  # get rid of center now
            'stim_colors': stim_colors,
            'test_color': test_color,
            'test_location': test_location,
        }

        return trial

    def display_break(self):
        break_text = 'Please take a short break. Press space to continue.'
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204])

    def display_fixation(self, wait_time):
        psychopy.visual.TextStim(
            self.experiment_window, text='+', color=[-1, -1, -1]).draw()
        self.experiment_window.flip()

        psychopy.core.wait(wait_time)

    def display_stimuli(self, coordinates, colors):
        psychopy.visual.TextStim(
            self.experiment_window, text='+', color=[-1, -1, -1]).draw()

        for pos, color in itertools.izip(coordinates, colors):
            psychopy.visual.Rect(
                self.experiment_window, height=self.stim_size,
                width=self.stim_size, pos=pos, fillColor=color,
                units='deg').draw()

        self.experiment_window.flip()

        psychopy.core.wait(self.sample_time)

    def display_test(self, condition, coordinates, colors, test_loc, test_color):
        psychopy.visual.TextStim(
            self.experiment_window, text='+', color=[-1, -1, -1]).draw()

        if self.single_probe:
            psychopy.visual.Rect(
                self.experiment_window, width=self.stim_size,
                height=self.stim_size, pos=coordinates[test_loc],
                fillColor=colors[test_loc], units='deg').draw()

        else:
            for pos, color in itertools.izip(coordinates, colors):
                psychopy.visual.Rect(
                    self.experiment_window, width=self.stim_size,
                    height=self.stim_size, pos=pos, fillColor=color,
                    units='deg').draw()

        # Draw over the test color on diff trials
        if condition == 'diff':
            psychopy.visual.Rect(
                self.experiment_window, width=self.stim_size,
                height=self.stim_size, pos=coordinates[test_loc],
                fillColor=test_color, units='deg').draw()

        self.experiment_window.flip()

        psychopy.core.wait(self.sample_time)

    def get_response(self, ):
        rt_timer = psychopy.core.MonotonicClock()

        keys = self.keys + ['q']

        resp = psychopy.event.waitKeys(keyList=keys, timeStamped=rt_timer)

        if 'q' in resp[0]:
            self.quit_experiment()

        return resp[0][0], resp[0][1]*1000  # key and rt in milliseconds

    def run_trial(self, trial, block_num, trial_num):
        coordinates = [[(num - .5) * self.allowed_deg_from_fix for num in loc]
                       for loc in trial['locations']]

        self.display_fixation(self.iti_time)
        self.display_stimuli(coordinates, trial['stim_colors'])
        self.display_fixation(self.delay_time)
        self.display_test(
            trial['condition'], coordinates, trial['stim_colors'],
            trial['test_location'], trial['test_color'])

        resp, rt = self.get_response()

        acc = 1 if resp == trial['cresp'] else 0

        self.update_experiment_data([{
            'Block': block_num,
            'Trial': trial_num,
            'Timestamp': psychopy.core.getAbsTime(),
            'Condition': trial['condition'],
            'SetSize': trial['set_size'],
            'RT': rt,
            'CRESP': trial['cresp'],
            'RESP': resp,
            'ACC': acc,
            'LocationTested': trial['test_location'],
            'Locations': trial['locations'],
            'SampleColors': trial['stim_colors'],
            'TestColor': trial['test_color'],
        }])

    def run(self):
        self.chdir()

        ok = self.get_experiment_info_from_dialog(questionaire_dict)

        if not ok:
            print('Experiment has been terminated.')
            sys.exit(1)

        self.save_experiment_info()
        self.open_csv_data_file()
        self.open_window(screen=0)
        self.display_text_screen('Loading...', wait_for_input=False)

        for instruction in self.instruct_text:
            self.display_text_screen(text=instruction)

        for block_num in range(self.number_of_blocks):
            block = self.make_block()
            for trial_num, trial in enumerate(block):
                self.run_trial(trial, block_num, trial_num)

            self.save_experiment_pickle()
            self.save_data_to_csv()

            if block_num + 1 != self.number_of_blocks:
                self.display_break()

        self.display_text_screen(
            'The experiment is now over, please get your experimenter.',
            bg_color=[0, 0, 255], text_color=[255, 255, 255])

        self.quit_experiment()

# If you call this script directly, the task will run with your defaults
if __name__ == '__main__':
    exp = Ktask(
        # BaseExperiment parameters
        experiment_name=exp_name,
        data_fields=data_fields,
        monitor_distance=distance_to_monitor,
        # Custom parameters go here
    )

    exp.run()
