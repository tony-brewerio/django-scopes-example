from django.db import models

from django.db.models.query import QuerySet
from django.db.models.base import ModelBase


class ScopedModelBase(ModelBase):

    def __new__(cls, name, bases, attrs):

        scopes_bases = filter(None, [attrs.get('Scopes')] + 
                                    [getattr(b, 'Scopes', None) for b in bases])

        attrs['Scopes'] = type('ScopesFor' + name, tuple(scopes_bases), {})

        ScopedQuerySet = type('ScopedQuerySetFor' + name, (QuerySet, attrs['Scopes']), {})
        ScopedManager = type('ScopedManagerFor' + name, (models.Manager, attrs['Scopes']), {
            'use_for_related_fields': True,
            'get_query_set': lambda self: ScopedQuerySet(self.model, using = self._db)
        })
        
        attrs['objects'] = ScopedManager()

        return ModelBase.__new__(cls, name, bases, attrs)


class ScopedModel(models.Model):
    
    __metaclass__ = ScopedModelBase
    
    class Meta:
        abstract = True

    class Scopes(object): 
        pass
    
    
        
class Pet(ScopedModel):
    
    class Meta:
        db_table = 'pet'

    class Scopes:
        
        def male(self):
            return self.filter(sex = 'm')
        def female(self):
            return self.filter(sex = 'f')
            
        def cats(self):
            return self.filter(species = 'cat')
            
        @property
        def dead(self):
            return self.exclude(death = None)
        @property
        def alive(self):
            return self.filter(death = None)    
        
    
    
    name = models.TextField()
    owner = models.TextField()
    species = models.TextField()
    sex = models.TextField()
    
    birth = models.DateTimeField()
    death = models.DateTimeField()

    def __unicode__(self):
        return "%s, %s, %s, %s" % (self.name, self.owner, self.species, self.sex)    
        
        
Pet.Scopes.mammals = lambda self: self.filter(species__in = ['cats', 'dog'])
