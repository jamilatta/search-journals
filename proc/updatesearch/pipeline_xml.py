# coding: utf-8
from lxml import etree as ET

import plumber


"""
Full example output of this pipeline:

    <doc>
        <field name="id">art-S0102-695X2015000100053-scl</field>
        <field name="journal_title">Revista Ambiente & Água</field>
        <field name="in">scl</field>
        <field name="ac">Agricultural Sciences</field>
        <field name="type">editorial</field>
        <field name="ur">art-S1980-993X2015000200234</field>
        <field name="authors">Marcelo dos Santos, Targa</field>
        <field name="ti_*">Benefits and legacy of the water crisis in Brazil</field>
        <field name="pg">234-239</field>
        <field name="doi">10.1590/S0102-67202014000200011</field>
        <field name="wok_citation_index">SCIE</field>
        <field name="volume">48</field>
        <field name="supplement_volume">48</field>
        <field name="issue">7</field>
        <field name="supplement_issue">suppl. 2</field>
        <field name="start_page">216</field>
        <field name="end_page">218</field>
        <field name="ta">Rev. Ambient. Água</field>
        <field name="la">en</field>
        <field name="fulltext_pdf_pt">http://www.scielo.br/pdf/ambiagua/v10n2/1980-993X-ambiagua-10-02-00234.pdf</field>
        <field name="fulltext_pdf_pt">http://www.scielo.br/scielo.php?script=sci_abstract&pid=S0102-67202014000200138&lng=en&nrm=iso&tlng=pt</field>
        <field name="da">2015-06</field>
        <field name="ab_*">In this editorial, we reflect on the benefits and legacy of the water crisis....</field>
        <field name="aff_country">Brasil</field>
        <field name="aff_institution">usp</field>
        <field name="sponsor">CNPQ</field>
    </doc>
"""


class SetupDocument(plumber.Pipe):

    def transform(self, data):
        xml = ET.Element('doc')

        return data, xml


class DocumentID(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = '{0}-{1}'.format(raw.publisher_id, raw.collection_acronym)
        field.set('name', 'id')

        xml.find('.').append(field)

        return data


class JournalTitle(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.journal.title
        field.set('name', 'journal_title')

        xml.find('.').append(field)

        return data


class Collection(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.collection_acronym
        field.set('name', 'in')

        xml.find('.').append(field)

        return data


class KnowledgeArea(plumber.Pipe):

    def precond(data):
        raw, xml = data

        if not raw.subject_areas:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        for item in raw.subject_areas:
            field = ET.Element('field')
            field.text = item
            field.set('name', 'ac')

            xml.find('.').append(field)

        return data


class DocumentType(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.document_type
        field.set('name', 'type')

        xml.find('.').append(field)

        return data


class URL(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = '{0}'.format(raw.publisher_id)
        field.set('name', 'ur')

        xml.find('.').append(field)

        return data


class Authors(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.authors:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        for author in raw.authors:
            field = ET.Element('field')
            name = []
            if 'given_names' in author:
                name.append(author['given_names'])

            if 'surname' in author:
                name.append(author['surname'])

            field.text = ', '.join(name)

            field.set('name', 'au')
            xml.find('.').append(field)

        return data


class OriginalTitle(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.original_title():
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.original_title()
        field.set('name', 'ti')
        xml.find('.').append(field)

        return data


class Titles(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.original_title() and not raw.translated_titles():
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.original_title()
        field.set('name', 'ti_%s' % raw.original_language())
        xml.find('.').append(field)

        if not raw.translated_titles():
            return data

        for language, title in raw.translated_titles().items():
            field = ET.Element('field')
            field.text = title
            field.set('name', 'ti_%s' % language)
            xml.find('.').append(field)

        return data


class Pages(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.start_page and not raw.end_page:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        pages = []

        if raw.start_page:
            pages.append(raw.start_page)

        if raw.end_page:
            pages.append(raw.end_page)

        field = ET.Element('field')
        field.text = '-'.join(pages)
        field.set('name', 'pg')
        xml.find('.').append(field)

        return data


class DOI(plumber.Pipe):

    def precond(data):
        raw, xml = data

        if not raw.doi:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.doi
        field.set('name', 'doi')
        xml.find('.').append(field)

        return data


class WOKCI(plumber.Pipe):

    def precond(data):
        raw, xml = data

        if not raw.wos_citation_indexes:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        for index in raw.wos_citation_indexes:
            field = ET.Element('field')
            field.text = index.replace('&', '')
            field.set('name', 'wok_citation_index')
            xml.find('.').append(field)

        return data


class WOKSC(plumber.Pipe):

    def precond(data):
        raw, xml = data

        if not raw.wos_subject_areas:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        for index in raw.wos_subject_areas:
            field = ET.Element('field')
            field.text = index
            field.set('name', 'wok_subject_categories')
            xml.find('.').append(field)

        return data


class Volume(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        if raw.volume:
            field = ET.Element('field')
            field.text = raw.volume
            field.set('name', 'volume')
            xml.find('.').append(field)

        return data


class SupplementVolume(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        if raw.supplement_volume:
            field = ET.Element('field')
            field.text = raw.supplement_volume
            field.set('name', 'supplement_volume')
            xml.find('.').append(field)

        return data


class Issue(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        if raw.issue:
            field = ET.Element('field')
            field.text = raw.issue
            field.set('name', 'issue')
            xml.find('.').append(field)

        return data


class SupplementIssue(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        if raw.supplement_issue:
            field = ET.Element('field')
            field.text = raw.supplement_issue
            field.set('name', 'supplement_issue')
            xml.find('.').append(field)

        return data


class ElocationPage(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.elocation:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.elocation
        field.set('name', 'elocation')
        xml.find('.').append(field)

        return data


class StartPage(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.start_page:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.start_page
        field.set('name', 'start_page')
        xml.find('.').append(field)

        return data


class EndPage(plumber.Pipe):

    def precond(data):

        raw, xml = data

        if not raw.end_page:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.end_page
        field.set('name', 'end_page')
        xml.find('.').append(field)

        return data


class JournalAbbrevTitle(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.journal_abbreviated_title
        field.set('name', 'ta')
        xml.find('.').append(field)

        return data


class AvailableLanguages(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        langs = set([i for i in raw.languages()])
        langs.add(raw.original_language())

        for language in langs:
            field = ET.Element('field')
            field.text = language
            field.set('name', 'la')
            xml.find('.').append(field)

        return data


class Fulltexts(plumber.Pipe):

    def precond(data):
        raw, xml = data

        if not raw.fulltexts():
            raise plumber.UnmetPrecondition()

    def transform(self, data):
        raw, xml = data

        ft = raw.fulltexts()

        # There is articles that does not have pdf
        if 'pdf' in ft:
            for language, url in ft['pdf'].items():

                field = ET.Element('field')
                field.text = url
                field.set('name', 'fulltext_pdf_%s' % language)
                xml.find('.').append(field)

        if 'html' in ft:
            for language, url in ft['html'].items():

                field = ET.Element('field')
                field.text = url
                field.set('name', 'fulltext_html_%s' % language)
                xml.find('.').append(field)

        return data


class PublicationDate(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.publication_date
        field.set('name', 'da')
        xml.find('.').append(field)

        return data


class Abstract(plumber.Pipe):

    def precond(data):
        raw, xml = data

        if not raw.original_abstract() and not raw.translated_abstracts():
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        field = ET.Element('field')
        field.text = raw.original_abstract()
        field.set('name', 'ab_%s' % raw.original_language())
        xml.find('.').append(field)

        if not raw.translated_abstracts():
            return data

        for language, abstract in raw.translated_abstracts().items():
            field = ET.Element('field')
            field.text = abstract
            field.set('name', 'ab_%s' % language)
            xml.find('.').append(field)

        return data


class AffiliationCountry(plumber.Pipe):

    def precond(data):
        raw, xml = data
        if not raw.mixed_affiliations:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        countries = set()

        for affiliation in raw.mixed_affiliations:
            if 'country' in affiliation:
                countries.add(affiliation['country'])

        for country in countries:
            field = ET.Element('field')
            field.text = country.strip()
            field.set('name', 'aff_country')
            xml.find('.').append(field)

        return data


class AffiliationInstitution(plumber.Pipe):

    def precond(data):
        raw, xml = data
        if not raw.mixed_affiliations:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        institutions = set()

        for affiliation in raw.mixed_affiliations:
            if 'institution' in affiliation:
                institutions.add(affiliation['institution'])

        for institution in institutions:
            field = ET.Element('field')
            field.text = institution.strip()
            field.set('name', 'aff_institution')
            xml.find('.').append(field)

        return data


class Sponsor(plumber.Pipe):

    def precond(data):
        raw, xml = data
        if not raw.project_sponsor:
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        sponsors = set()

        for sponsor in raw.project_sponsor:
            if 'orgname' in sponsor:
                sponsors.add(sponsor['orgname'])

        for sponsor in sponsors:
            field = ET.Element('field')
            field.text = sponsor
            field.set('name', 'sponsor')
            xml.find('.').append(field)

        return data


class TearDown(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        return xml
