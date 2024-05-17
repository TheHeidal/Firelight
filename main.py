# This is a sample Python script.
import collections
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
import string
import pathlib
import collections
import logging
import datetime

import json5


# with open(BOH_FOLDER + 'elements\\aspecteditems.json', 'r', encoding='utf-16') as j:
#     aspecteditems_elements = json.load(j)['elements']


def read_json(path):
    """Reads a BoH .json file and returns the dictionary of elements"""
    try:
        try:
            with open(path, 'r', encoding='utf-8-sig') as j:
                return json.load(j)['elements']
        except UnicodeError:
            logger.warning(f'utf-8 failed on {path}')
            with open(path, 'r', encoding='utf-16') as j:
                return json.load(j)['elements']
    except json.decoder.JSONDecodeError:
        logger.warning(f'JSONDecodeError reading {path}')
        try:
            with open(path, 'r', encoding='utf-16') as j:
                return json5.load(j)['elements']
        except UnicodeError:
            with open(path, 'r', encoding='utf-8-sig') as j:
                return json5.load(j)['elements']


def strip_punctuation(s):
    return s.translate(s.maketrans('', '', string.punctuation + string.whitespace))


def make_tag(s):
    return f'#{strip_punctuation(s)}'


def make_link(s: str):
    if any(char in s for char in '#^[]|'):
        raise ValueError(s)
    return f'[[{s}]]'


class Xtrigger:
    """Cross triggers are actions that can occur when recipes complete.

    XTriggers have two parts: A catalyst and an effects list.
        The catalyst is the id of an aspect that must be present for the effects to happen
        The effects is a list of effects that will happen if the catalyst is present.
    """

    def __init__(self, catalyst: str, product: str | list):
        """Create a xtrigger from parsed JSON

        catalyst: an ID
        product: either a list of effects or a str (representing tranform 1 str)
        """
        self.catalyst = catalyst
        self.effects: list[Effect] = []
        if type(product) is str:
            self.effects.append(Effect(id=product))
        elif type(product) is list:
            for effect in product:
                if type(effect) is str:
                    self.effects.append(Effect(id=product))
                elif type(effect) is dict:
                    self.effects.append(Effect(**effect))
                else:
                    raise TypeError('effect is not a str or dict', effect, catalyst, product)

    def markdownify(self):
        """Format a xtrigger into markdown.

        the final format is:
        - {backlinked Catalyst id}:
        \tab- morpheffect level {backlinked result id} chance

        omitting chance if it is 100, and
        omitting everything but result id if it's the default effect.
        """
        return f'\n- {make_link(self.catalyst)}:\n	- ' \
               + '\n	- '.join([effect.markdownify() for effect in self.effects])


class Effect:
    """A Xtrigger effect is a thing that can happen after a recipe completes.
    """

    def __init__(self, morpheffect='transform', id=None, level=1, chance=100, additive=False):
        self.morpheffect = morpheffect
        self.id = id
        self.level = level
        self.chance = chance
        self.additive = additive

    def markdownify(self):
        """Format an effect into markdown.

        the final format is:
        - {backlinked Catalyst id}:
        \tab- morpheffect level {backlinked result id} chance

        omitting chance if it is 100, and
        omitting everything but result id if it's the default effect.
        """
        try:
            link = make_link(self.id)
        except ValueError:
            link = f'[[{self.id}]] #badlink'
        if (self.morpheffect == 'transform') and (self.level == 1) and (self.chance == 100):
            return link
        else:
            return ' '.join([self.morpheffect.capitalize(),
                             str(self.level),
                             link,
                             str(self.chance if self.chance != 100 else '')])


class Element(collections.UserDict):
    """An element from Book of Hours.

    For reference, consult https://docs.google.com/document/d/1BZiUrSiT8kKvWIEvx5DObThL4HMGVI1CluJR20CWBU0/edit?usp=sharing

    In the JSONs, elements are represented as dictionaries. The possible keys are:

    ID: str
        the unique identifier of the element
    label: str
        the displayed name of the element
    Desc: str
        the displayed description of the element
    isAspect : bool
        whether the element can exist independently or
        has to be attached to another. Only used to find art
    icon : str
        the name of the file for the icon of this element.
    xtriggers : dict
        xtriggers ('cross triggers') are effects that occur at the end of
            recipes if the catalyst is present. They are in the format
        {Catalyst (an ID) :
            [morpheffect (mandatory),
               ID,
               level=1,
               chance=100
               ]
        or
        {Catalyst (an ID) : ID},  which transforms the element into
            the second ID, keeping any mutations
    induces, decayTo, verbicon, achievements.
        TODO Not yet implemented.

    Aspect-specific properties:

    isHidden : bool
        whether the aspect appears in any in-game aspect lists
    noArtNeeded : bool
        whether the game should search for artwork for this element

    Card-specific properties:

    aspects : dict
      (ID, int) pairs of IDs for aspects and their amounts
    inherits : ID
          the label of an element in _prototypes.json
    audio : str
          probably the label of something from the .resource files
    xexts : dict
      (ID, str) pairs TODO documentation of xexts
    unique : bool
        whether only one card can be present, and spawning a new card destroys the old one.
    uniquenessgroup : ID

    ambits : dict
      (ID, int) pairs
      TODO: figure ambits out. Can we just ignore them?
    """

    def __init__(self, json_dict: dict, parent_map: dict):
        """Creates an Element

        Args:
            json_dict: A json-derived dict representation of the element.
            parent_map: A dict containing any elements this inherits from.
        """
        # TODO: dict unpacking to handle all the properties individually?
        super().__init__(json_dict)
        self.parent_map = parent_map
        self.hasInherited = False

    @property
    def parent(self):
        return self.parent_map[self['inherits']]

    def bequeath(self, chain=None) -> dict | None:
        """Ensure that this element has inherited, then return its aspects"""
        if chain is None:
            chain = []

        if self['ID'] in chain: raise RecursionError(self, chain)
        if 'inherits' in self and not self.hasInherited:
            self.inherit(chain.append(self['ID']))

        if 'aspects' in self:
            return self['aspects']
        else:
            return None

    def inherit(self, chain=None):
        """Ensure that the element has its parents aspects"""
        # TODO: give parents a list of their children
        if chain is None:
            chain = []

        if self.hasInherited:
            return

        inherited_aspects = self.parent.bequeath(chain.append(self['ID']))

        if inherited_aspects is not None:
            if 'aspects' not in self:
                self['aspects'] = inherited_aspects
            else:
                for aspect, amount in inherited_aspects.items():
                    if aspect not in self['aspects']:
                        self['aspects'][aspect] = amount
                    # if aspects overlap between parent and child, child wins
                    # this prevents things becoming doubly considerable.
        self.hasInherited = True

    def markdownify(self):
        """Create a markdown representation of the Element.

        An example of the target format can be seen in dog.hungry.md
        """
        logging.debug(f'markdownifying {self}')

        def property_yesno(key: str) -> str:
            """Checks boolean parameters, 'Yes' if true, otherwise 'No'"""
            try:
                if self[key] is True: return 'Yes'
            except:
                pass
            return 'No'

        def markdownify_str_property(display='Label', key='Label') -> str:
            """Format a property only consisting of a string into Markdown

            Format is:
            display:
            - self[key]"""
            if key in self:
                return f"""{display}:\n- {self[key]}"""
            else:
                return f"{display}: *None*"

        def markdownify_xexts() -> str:
            """Format cross texts into markdown.

            the final format is:
            Cross texts:
            - {backlinked id}
                - {description string}
            - ...
            """
            try:
                ret_str = "Cross texts:"
                for id, text in self['xexts'].items():
                    ret_str += f"""
- {make_link(id)}
    - {text}"""
                return ret_str
            except KeyError:
                return ""

        def markdownify_aspects() -> str:
            try:
                aspect_list = ", ".join((f'{make_link(id)}: {val}'
                                         for id, val in self['aspects'].items()))

                return f"Aspects:\n- {aspect_list}"
            except KeyError:
                return "Aspects: *None*"

        def markdownify_xtriggers() -> str:
            """Format xtriggers into markdown.

            the final format is:
            Triggered by:
            - {backlinked Catalyst id}
            \tab- morpheffect level {backlinked result id} chance

            omitting chance if it is 100, and
            omitting everything but result id if it's the default effect.
            """
            try:
                ret_str = "Cross triggers:"
                for catalyst, product in self['xtriggers'].items():
                    ret_str += Xtrigger(catalyst, product).markdownify()
                return ret_str
            except KeyError:
                return "Cross triggers: None"

        def markdownify_xtriggers_reverse() -> str:
            # TODO: implement storing results of xtriggers
            return "Triggered from: Not Implemented"

        def markdownify_slots() -> str:
            # TODO implement slots, which will likely mean implementing more inheritance
            return 'Induces: Not Implemented'

        def markdownify_inherits() -> str:
            try:
                return f'''Inherits: {make_link(self.parent['ID'])}'''
            except KeyError:
                return f'Inherits: *None*'

        def markdownify_inherits_reverse() -> str:
            # TODO: implement storing results of xtriggers
            return "Inherited by: Not Implemented"

        def markdownify_value(display, key) -> str:
            try:
                return f'''{display}: {self[key]}'''
            except KeyError:
                return f'{display}: *None*'

        def markdownify_booleans(display='Unique', key='unique') -> str:
            return f'''{display}?: {property_yesno(key)}'''

        def markdownify_id(display='Uniqueness Group', key='uniquenessgroup') -> str:
            try:
                return f'''{display}: {make_link(self[key])}'''
            except KeyError:
                return f'{display}: *None*'

        return "\n\n".join([markdownify_str_property(display='ID', key='ID'),
                            markdownify_str_property(display='Label', key='Label'),
                            markdownify_str_property(display='Description', key='desc'),
                            markdownify_xexts(),
                            markdownify_aspects(),
                            markdownify_xtriggers(),
                            markdownify_xtriggers_reverse(),
                            markdownify_slots(),
                            markdownify_inherits(),
                            markdownify_inherits_reverse(),
                            markdownify_value(display="Induces", key='induce'),
                            markdownify_id(display='Audio', key='audio'),
                            markdownify_value(display='Lifetime', key='lifetime'),
                            markdownify_id(display='Decay to', key='decayto'),
                            markdownify_booleans(display='Unique', key='unique'),
                            markdownify_id(display='Uniqueness Group', key='uniquenessgroup'),
                            markdownify_booleans(display='Aspect', key='aspect'),
                            markdownify_booleans(display='Hidden', key='isHidden'),
                            markdownify_booleans(display='No Art Needed', key='noartneeded'),
                            markdownify_booleans(display='Resaturate', key='resaturate')])


JSON_DIRECTORY = r'C:\Program Files (x86)\Steam\steamapps\common\Book of Hours\bh_Data\StreamingAssets\bhcontent\core\elements'

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    now = datetime.datetime.now().strftime('%y-%m-%d %H%M%S')
    logging.basicConfig(filename=f'C:/Users/jphei/PycharmProjects/Firelight/{now}.log',
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format="%(asctime)s %(name)-30s %(levelname)-8s %(message)s")

    # get list of json files
    # TODO: implement all JSONs, currently only reads the Elements folder
    with pathlib.Path(JSON_DIRECTORY) as directory:
        json_paths_generator = (path for path in directory.iterdir() if path.suffix == '.json')
        logger.info(f'reading files in {directory}')

    # create a dictionary of elements by ID
    # and a list of elements that need to receive inheritance
    elements_dict = {}
    needs_inheritance = []
    #  iterate through the JSONs, adding every element to the elements dict
    for json_path in json_paths_generator:
        curr_elements = read_json(json_path)
        logger.info(f'read JSON at {json_path}')
        for json_element in curr_elements:
            # sometimes ID is 'id' in the JSONs.
            try:
                elements_dict[json_element['ID']] = Element(json_element, elements_dict)
            except KeyError:
                json_element['ID'] = json_element['id']
                elements_dict[json_element['ID']] = Element(json_element, elements_dict)
            # while adding elements, maintain a queue of elements that inherit
            if 'inherits' in json_element:
                needs_inheritance.append(json_element['ID'])
    # iterate through the queue, for each element adding inherited properties
    for element_id in needs_inheritance:
        elements_dict[element_id].inherit()

    for element_id in iter(elements_dict):
        #     element_id = 'dog.hungry'
        try:
            with open(fr'C:\Users\jphei\OneDrive\Documents\Book of Hours\Firelight\{element_id}.md',
                      mode='w', encoding='utf-8') as f:
                f.write(elements_dict[element_id].markdownify())
        except FileExistsError:
            pass
        logging.info(f'Created {element_id}!')

    pass
