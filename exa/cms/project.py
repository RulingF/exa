# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Project Table
#################
A project represents a continuous program or finite study of a subject. It is
the highest level of categorical organization for content management. A project
may have any number of associated :class:`~exa.cms.job.Job` and
:class:`~exa.cms.files.File` objects.
"""
from sqlalchemy import Integer, Column, ForeignKey, Table
from sqlalchemy.orm import relationship
from exa.cms.base import Base, Name, Time, Size


project_job = Table(   # Many to many relationship; Project - Job
    'project_job',
    Base.metadata,
    Column(
        'project_pkid',
        Integer,
        ForeignKey('project.pkid', onupdate='CASCADE', ondelete='CASCADE')
    ),
    Column(
        'job_pkid',
        Integer,
        ForeignKey('job.pkid', onupdate='CASCADE', ondelete='CASCADE')
    )
)


project_file = Table(    # Many to many relationship; Project - DataFile
    'project_file',
    Base.metadata,
    Column(
        'project_pkid',
        Integer,
        ForeignKey('project.pkid', onupdate='CASCADE', ondelete='CASCADE')
    ),
    Column(
        'file_pkid',
        Integer,
        ForeignKey('file.pkid', onupdate='CASCADE', ondelete='CASCADE')
    )
)


class Project(Name, Time, Size, Base):
    """An ongoing program or finite study."""
    jobs = relationship('Job', secondary=project_job, backref='projects',
                        cascade='all, delete')
    files = relationship('File', secondary=project_file,
                         backref='projects', cascade='all, delete')

    @property
    def list_files(self):
        """Get all files associated with this project (i.e. job files)."""
        files = self.files
        for job in self.jobs:
            files += job.files
        return files
