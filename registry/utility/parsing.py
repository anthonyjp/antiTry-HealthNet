import os
import xml.etree.cElementTree

from registry.models import MedicalCondition
from HealthNet.settings import BASE_DIR


def parse_conditions(filename):
    """
    Takes an XML File containing conditions and parses them into the database.
    If the condition already exists but it's description differs from the new description,
    it's description is changed. If they are identical, no change occurs.

    The XML File must be of the form:

    <conditions>
        <condition name="...">
            ...
        </condition>\n
        ...
    </conditions>

    :param filename: XML File containing Conditions
    """
    tree = xml.etree.cElementTree.parse(os.path.join(BASE_DIR, filename)).getroot()

    for condition in tree.findall('condition'):
        name = condition.get('name').strip()
        text = condition.text.strip()

        if text is not None:
            registered_conditions = MedicalCondition.objects.filter(name=name)
            if not MedicalCondition.objects.filter(name=name).exists():
                MedicalCondition.objects.create(name=name, desc=text)
            else:
                elem = registered_conditions.first()
                if elem.desc != text:
                    elem.desc = text
                    elem.save()
