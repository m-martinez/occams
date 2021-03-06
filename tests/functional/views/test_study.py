import pytest
from tests.testing import USERID, make_environ, get_csrf_token


class TestPermissionsStudyList:

    url = '/'

    @pytest.fixture(autouse=True)
    def populate(self, app, dbsession):
        import transaction
        from occams import models

        # Any view-dependent data goes here
        # Webtests will use a different scope for its transaction
        with transaction.manager:
            dbsession.add(models.User(key=USERID))

    @pytest.mark.parametrize('group', [
        'administrator', 'manager', 'enterer', 'reviewer',
        'consumer', 'member', None])
    def test_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.get(self.url, extra_environ=environ)
        assert 200 == res.status_code

    def test_not_authenticated(self, app):
        app.get(self.url, status=401)


class TestPermissionsStudyAdd:

    url = '/'

    @pytest.fixture(autouse=True)
    def populate(self, app, dbsession):
        import transaction
        from occams import models

        # Any view-dependent data goes here
        # Webtests will use a different scope for its transaction
        with transaction.manager:
            user = models.User(key=USERID)
            dbsession.info['blame'] = user
            dbsession.add(user)
            dbsession.flush()

    @pytest.mark.parametrize('group', ['administrator', 'manager'])
    def test_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {'name': u'test',
                'title': u'test_title',
                'short_title': u'test2',
                'code': u'test3',
                'consent_date': '2015-01-01'}

        res = app.post_json(
            self.url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token
            },
            params=data)
        assert 200 == res.status_code

    @pytest.mark.parametrize('group', [
        'enterer', 'reviewer', 'consumer', 'member', None])
    def test_not_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.post(
            self.url,
            extra_environ=environ,
            xhr=True,
            status='*')
        assert 403 == res.status_code

    def test_not_authenticated(self, app):
        app.post(self.url, status=401)


class TestPermissionsStudyView:

    study = 'test'
    url = '/studies/{}'.format(study)

    @pytest.fixture(autouse=True)
    def populate(self, app, dbsession):
        import transaction
        from occams import models
        from datetime import date

        # Any view-dependent data goes here
        # Webtests will use a different scope for its transaction
        with transaction.manager:
            user = models.User(key=USERID)
            dbsession.info['blame'] = user
            dbsession.add(user)
            dbsession.flush()
            dbsession.add(models.Study(
                name=u'test',
                title=u'test',
                short_title=u'test',
                code=u'test',
                consent_date=date.today(),
                is_randomized=False))

    @pytest.mark.parametrize('group', [
        'administrator', 'manager', 'enterer', 'reviewer',
        'consumer', 'member', None])
    def test_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.get(self.url, extra_environ=environ)
        assert 200 == res.status_code

    def test_not_authenticated(self, app):
        app.get(self.url, status=401)


class TestPermissionsStudyEdit:

    study = 'test'
    url = '/studies/{}'.format(study)

    @pytest.fixture(autouse=True)
    def populate(self, app, dbsession):
        import transaction
        from occams import models
        from datetime import date

        # Any view-dependent data goes here
        # Webtests will use a different scope for its transaction
        with transaction.manager:
            user = models.User(key=USERID)
            dbsession.info['blame'] = user
            dbsession.add(user)
            dbsession.flush()
            dbsession.add(
                models.Study(
                    name=u'test',
                    title=u'test',
                    short_title=u'test',
                    code=u'test',
                    consent_date=date.today(),
                    is_randomized=False))

    @pytest.mark.parametrize('group', ['administrator', 'manager'])
    def test_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.get(self.url, extra_environ=environ, xhr=True)
        data = res.json

        csrf_token = get_csrf_token(app, environ)

        res = app.put_json(
            self.url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token
            },
            params=data)
        assert 200 == res.status_code

    @pytest.mark.parametrize('group', [
        'enterer', 'reviewer', 'consumer', 'member', None])
    def test_not_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.put(
            self.url,
            extra_environ=environ,
            xhr=True,
            status='*')
        assert 403 == res.status_code

    def test_not_authenticated(self, app):
        app.get(self.url, status=401)


class TestPermissionsStudyDelete:

    study = 'test'
    url = '/studies/{}'.format(study)

    @pytest.fixture(autouse=True)
    def populate(self, app, dbsession):
        import transaction
        from occams import models
        from datetime import date

        # Any view-dependent data goes here
        # Webtests will use a different scope for its transaction
        with transaction.manager:
            user = models.User(key=USERID)
            dbsession.info['blame'] = user
            dbsession.add(user)
            dbsession.flush()
            dbsession.add(
                models.Study(
                    name=u'test',
                    title=u'test',
                    short_title=u'test',
                    code=u'test',
                    consent_date=date.today(),
                    is_randomized=False))

    @pytest.mark.parametrize('group', ['administrator', 'manager'])
    def test_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.get(self.url, extra_environ=environ, xhr=True)
        data = res.json
        csrf_token = get_csrf_token(app, environ)

        res = app.delete_json(
            self.url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token
            },
            params=data)

        assert 200 == res.status_code

    @pytest.mark.parametrize('group', [
        'enterer', 'reviewer', 'consumer', 'member', None])
    def test_not_allowed(self, app, dbsession, group):
        environ = make_environ(userid=USERID, groups=[group])
        res = app.get(self.url, extra_environ=environ, xhr=True)
        data = res.json
        csrf_token = get_csrf_token(app, environ)

        res = app.delete_json(
            self.url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token,
                'X-REQUESTED-WITH': str('XMLHttpRequest')
            },
            params=data)

        assert 403 == res.status_code

    def test_not_authenticated(self, app):
        app.delete(self.url, status=401)
