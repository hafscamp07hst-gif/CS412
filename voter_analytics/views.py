# File: voter_analytics/views.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/30/2026
# Description: Display, filter, and graph voter records.

import plotly
import plotly.graph_objs as go

from django.views.generic import ListView, DetailView
from .models import Voter


class VoterListView(ListView):
    """Display voter records with optional search criteria."""

    template_name = 'voter_analytics/voters.html'
    model = Voter
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        """Return voters matching the selected GET search criteria."""
        voters = super().get_queryset().order_by('pk')

        # Apply each criterion only when the form supplies a value.
        party = self.request.GET.get('party', '')
        if party:
            voters = voters.filter(party_affiliation=party)

        min_year = self.request.GET.get('min_year', '')
        max_year = self.request.GET.get('max_year', '')
        years = [str(year) for year in range(1900, 2027)]
        # Use the neighboring years to include January 1 and December 31.
        if min_year in years:
            voters = voters.filter(date_of_birth__gt=f'{int(min_year) - 1}-12-31')
        if max_year in years:
            voters = voters.filter(date_of_birth__lt=f'{int(max_year) + 1}-01-01')

        score = self.request.GET.get('score', '')
        if score in ['0', '1', '2', '3', '4', '5']:
            voters = voters.filter(voter_score=score)

        # Selected elections must all be True; unchecked ones are unrestricted.
        if self.request.GET.get('v20state') == 'on':
            voters = voters.filter(v20state=True)
        if self.request.GET.get('v21town') == 'on':
            voters = voters.filter(v21town=True)
        if self.request.GET.get('v21primary') == 'on':
            voters = voters.filter(v21primary=True)
        if self.request.GET.get('v22general') == 'on':
            voters = voters.filter(v22general=True)
        if self.request.GET.get('v23town') == 'on':
            voters = voters.filter(v23town=True)

        return voters

    def get_context_data(self, **kwargs):
        """Add search choices and values to the template context using kwargs."""
        context = super().get_context_data(**kwargs)
        # Keep the two-character party codes exactly as stored in the CSV.
        context['parties'] = [
            'A ', 'AA', 'CC', 'D ', 'E ', 'EE', 'FF', 'G ', 'GG',
            'H ', 'HH', 'J ', 'K ', 'L ', 'O ', 'P ', 'Q ', 'R ',
            'S ', 'T ', 'U ', 'V ', 'W ', 'X ', 'Y ', 'Z ',
        ]
        context['years'] = [str(year) for year in range(1900, 2027)]
        context['scores'] = ['0', '1', '2', '3', '4', '5']

        # Reuse selected values in the form and pagination links.
        for field in ['party', 'min_year', 'max_year', 'score',
                      'v20state', 'v21town', 'v21primary',
                      'v22general', 'v23town']:
            context[field] = self.request.GET.get(field, '')
        return context


class VoterDetailView(DetailView):
    """Display all stored fields for one voter."""

    template_name = 'voter_analytics/voter.html'
    model = Voter
    context_object_name = 'voter'


class VoterGraphsView(VoterListView):
    """Graph all voters matching the same search criteria as the list."""

    template_name = 'voter_analytics/graphs.html'
    paginate_by = None

    def get_context_data(self, **kwargs):
        """Add three Plotly graph divs to the template context (kwargs)."""
        context = super().get_context_data(**kwargs)
        voters = context['voters']
        # Use filter and len, as in the class runner-count examples.
        years = []
        counts = []
        for year in context['years']:
            year_voters = voters.filter(
                date_of_birth__gt=f'{int(year) - 1}-12-31',
                date_of_birth__lt=f'{int(year) + 1}-01-01',
            )
            if len(year_voters) > 0:
                years.append(int(year))
                counts.append(len(year_voters))

        fig = go.Bar(x=years, y=counts)
        context['graph_birth_years'] = plotly.offline.plot(
            {'data': [fig], 'layout_title_text': 'Voters by Birth Year'},
            auto_open=False,
            output_type='div',
        )

        # Show each party's share of the matching voters.
        parties = []
        counts = []
        for party in context['parties']:
            party_voters = voters.filter(party_affiliation=party)
            if len(party_voters) > 0:
                parties.append(party)
                counts.append(len(party_voters))
        fig = go.Pie(labels=parties, values=counts, textinfo='none')
        context['graph_parties'] = plotly.offline.plot(
            {'data': [fig], 'layout_title_text': 'Voters by Party'},
            auto_open=False,
            output_type='div',
        )

        # Compare participation in the five elections from the CSV.
        elections = ['v20state', 'v21town', 'v21primary',
                     'v22general', 'v23town']
        election_counts = [
            len(voters.filter(v20state=True)),
            len(voters.filter(v21town=True)),
            len(voters.filter(v21primary=True)),
            len(voters.filter(v22general=True)),
            len(voters.filter(v23town=True)),
        ]
        fig = go.Bar(x=elections, y=election_counts)
        context['graph_elections'] = plotly.offline.plot(
            {'data': [fig], 'layout_title_text': 'Voters by Election'},
            auto_open=False,
            output_type='div',
        )
        context['voter_count'] = len(voters)
        return context
