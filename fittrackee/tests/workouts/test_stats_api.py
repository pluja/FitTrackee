import json

import pytest
from flask import Flask

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES


class TestGetStatsByTime(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/api/stats/{user_1.username}/by_time',
        )

        self.assert_401(response)

    def test_it_returns_error_if_user_is_authenticated_authenticated(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_2.username}/by_time',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_gets_no_stats_when_user_has_no_workouts(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {}

    def test_it_returns_error_when_user_does_not_exists(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/stats/1000/by_time',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_entity(response, 'user')

    def test_it_returns_error_if_date_format_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from="2018-04-01&to=2018-04-30'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response)

    def test_it_returns_error_if_period_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30&time=day'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'invalid time period', 'fail')

    def test_it_returns_error_if_stats_type_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time?from=2018-04-01'
                f'&to=2018-04-30&type={self.random_string()}'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'invalid stats type', 'fail')

    @pytest.mark.parametrize('input_type', ['', '?type=total'])
    def test_it_gets_stats_by_time_all_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
        input_type: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time{input_type}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017': {
                '1': {
                    'total_ascent': 220.0,
                    'total_descent': 280.0,
                    'total_distance': 15.0,
                    'total_duration': 4480,
                    'total_workouts': 2,
                }
            },
            '2018': {
                '1': {
                    'total_ascent': 340.0,
                    'total_descent': 500.0,
                    'total_distance': 39.0,
                    'total_duration': 11624,
                    'total_workouts': 5,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
        }

    def test_it_gets_stats_for_april_2018(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            }
        }

    def test_it_gets_stats_for_april_2018_with_paris_timezone(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.get(
            f'/api/stats/{user_1_paris.username}/by_time?'
            f'from=2018-04-01&to=2018-04-30',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            }
        }

    def test_it_gets_stats_by_year(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=year',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017': {
                '1': {
                    'total_ascent': 220.0,
                    'total_descent': 280.0,
                    'total_distance': 15.0,
                    'total_duration': 4480,
                    'total_workouts': 2,
                }
            },
            '2018': {
                '1': {
                    'total_ascent': 340.0,
                    'total_descent': 500.0,
                    'total_distance': 39.0,
                    'total_duration': 11624,
                    'total_workouts': 5,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
        }

    def test_it_gets_stats_by_year_for_april_2018(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30&time=year'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            }
        }

    def test_it_gets_stats_by_year_for_april_2018_with_paris_timezone(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1_paris.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30&time=year'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            }
        }

    def test_it_gets_stats_by_month(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=month',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03': {
                '1': {
                    'total_ascent': 120.0,
                    'total_descent': 200.0,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2017-06': {
                '1': {
                    'total_ascent': 100.0,
                    'total_descent': 80.0,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                    'total_workouts': 1,
                }
            },
            '2018-01': {
                '1': {
                    'total_ascent': 80.0,
                    'total_descent': 100.0,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2018-02': {
                '1': {
                    'total_ascent': 220.0,
                    'total_descent': 380.0,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                    'total_workouts': 2,
                }
            },
            '2018-04': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
            '2018-05': {
                '1': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                    'total_workouts': 1,
                }
            },
        }

    def test_it_gets_stats_by_month_with_new_york_timezone(
        self,
        app: Flask,
        user_1_full: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_full.email
        )

        response = client.get(
            f'/api/stats/{user_1_full.username}/by_time?time=month',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03': {
                '1': {
                    'total_ascent': 120.0,
                    'total_descent': 200.0,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2017-06': {
                '1': {
                    'total_ascent': 100.0,
                    'total_descent': 80.0,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                    'total_workouts': 1,
                }
            },
            '2018-01': {
                '1': {
                    'total_ascent': 80.0,
                    'total_descent': 100.0,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2018-02': {
                '1': {
                    'total_ascent': 220.0,
                    'total_descent': 380.0,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                    'total_workouts': 2,
                }
            },
            '2018-04': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
            '2018-05': {
                '1': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                    'total_workouts': 1,
                }
            },
        }

    def test_it_gets_stats_by_month_for_april_2018(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30&time=month'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018-04': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            }
        }

    def test_it_gets_stats_by_week(
        self,
        app: Flask,
        user_1_full: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_full.email
        )

        response = client.get(
            f'/api/stats/{user_1_full.username}/by_time?time=week',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03-19': {
                '1': {
                    'total_ascent': 120.0,
                    'total_descent': 200.0,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2017-05-28': {
                '1': {
                    'total_ascent': 100.0,
                    'total_descent': 80.0,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                    'total_workouts': 1,
                }
            },
            '2017-12-31': {
                '1': {
                    'total_ascent': 80.0,
                    'total_descent': 100.0,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2018-02-18': {
                '1': {
                    'total_ascent': 220.0,
                    'total_descent': 380.0,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                    'total_workouts': 2,
                }
            },
            '2018-04-01': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
            '2018-05-06': {
                '1': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                    'total_workouts': 1,
                }
            },
        }

    def test_it_gets_stats_by_week_for_week_13(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30&time=week'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018-04-01': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            }
        }

    def test_if_get_stats_by_week_starting_with_monday(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=weekm',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017-03-20': {
                '1': {
                    'total_ascent': 120.0,
                    'total_descent': 200.0,
                    'total_distance': 5.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2017-05-29': {
                '1': {
                    'total_ascent': 100.0,
                    'total_descent': 80.0,
                    'total_distance': 10.0,
                    'total_duration': 3456,
                    'total_workouts': 1,
                }
            },
            '2018-01-01': {
                '1': {
                    'total_ascent': 80.0,
                    'total_descent': 100.0,
                    'total_distance': 10.0,
                    'total_duration': 1024,
                    'total_workouts': 1,
                }
            },
            '2018-02-19': {
                '1': {
                    'total_ascent': 220.0,
                    'total_descent': 380.0,
                    'total_distance': 11.0,
                    'total_duration': 1600,
                    'total_workouts': 2,
                }
            },
            '2018-03-26': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
            '2018-04-02': {
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
            '2018-05-07': {
                '1': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 10.0,
                    'total_duration': 3000,
                    'total_workouts': 1,
                }
            },
        }

    def test_it_gets_stats_by_week_starting_with_monday_for_week_13(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            (
                f'/api/stats/{user_1.username}/by_time'
                f'?from=2018-04-01&to=2018-04-30&time=weekm'
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2018-03-26': {
                '1': {
                    'total_ascent': 40.0,
                    'total_descent': 20.0,
                    'total_distance': 8.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
            '2018-04-02': {
                '2': {
                    'total_ascent': None,
                    'total_descent': None,
                    'total_distance': 12.0,
                    'total_duration': 6000,
                    'total_workouts': 1,
                },
            },
        }

    def test_it_gets_average_stats_by_time_all_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?type=average',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017': {
                '1': {
                    'average_ascent': 110.0,
                    'average_descent': 140.0,
                    'average_distance': 7.5,
                    'average_duration': 2240,
                    'average_speed': 14.0,
                    'total_workouts': 2,
                }
            },
            '2018': {
                '1': {
                    'average_ascent': 85.0,
                    'average_descent': 125.0,
                    'average_distance': 7.8,
                    'average_duration': 2324,
                    'average_speed': 18.79,
                    'total_workouts': 5,
                },
                '2': {
                    'average_ascent': None,
                    'average_descent': None,
                    'average_distance': 12.0,
                    'average_duration': 6000,
                    'average_speed': 7.2,
                    'total_workouts': 1,
                },
            },
        }

    def test_it_gets_average_stats_by_year(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time?time=year&type=average',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '2017': {
                '1': {
                    'average_ascent': 110.0,
                    'average_descent': 140.0,
                    'average_distance': 7.5,
                    'average_duration': 2240,
                    'average_speed': 14.0,
                    'total_workouts': 2,
                }
            },
            '2018': {
                '1': {
                    'average_ascent': 85.0,
                    'average_descent': 125.0,
                    'average_distance': 7.8,
                    'average_duration': 2324,
                    'average_speed': 18.79,
                    'total_workouts': 5,
                },
                '2': {
                    'average_ascent': None,
                    'average_descent': None,
                    'average_distance': 12.0,
                    'average_duration': 6000,
                    'average_speed': 7.2,
                    'total_workouts': 1,
                },
            },
        }

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_time',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetStatsBySport(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport',
        )

        self.assert_401(response)

    def test_it_returns_error_if_user_is_authenticated_authenticated(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_2.username}/by_sport',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_gets_stats_by_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '1': {
                'average_ascent': 93.33,
                'average_descent': 130.0,
                'average_distance': 7.71,
                'average_duration': '0:38:20',
                'average_speed': 17.42,
                'total_ascent': 560.0,
                'total_descent': 780.0,
                'total_distance': 54.0,
                'total_duration': '4:28:24',
                'total_workouts': 7,
            },
            '2': {
                'average_ascent': None,
                'average_descent': None,
                'average_distance': 12.0,
                'average_duration': '1:40:00',
                'average_speed': 7.2,
                'total_ascent': None,
                'total_descent': None,
                'total_distance': 12.0,
                'total_duration': '1:40:00',
                'total_workouts': 1,
            },
        }

    def test_it_get_stats_for_sport_1(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport?sport_id=1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['statistics'] == {
            '1': {
                'average_ascent': 93.33,
                'average_descent': 130.0,
                'average_distance': 7.71,
                'average_duration': '0:38:20',
                'average_speed': 17.42,
                'total_ascent': 560.0,
                'total_descent': 780.0,
                'total_distance': 54.0,
                'total_duration': '4:28:24',
                'total_workouts': 7,
            }
        }

    def test_it_returns_error_if_sport_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport?sport_id=999',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_entity(response, 'sport')

    def test_it_returns_error_if_sport_id_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        seven_workouts_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport?sport_id="999',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            f'/api/stats/{user_1.username}/by_sport',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetAllStats(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get('/api/stats/all')

        self.assert_401(response)

    def test_it_returns_all_stats_when_users_have_no_workouts(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['workouts'] == 0
        assert data['data']['sports'] == 0
        assert data['data']['users'] == 2
        assert 'uploads_dir_size' in data['data']

    def test_it_gets_app_all_stats_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['workouts'] == 3
        assert data['data']['sports'] == 2
        assert data['data']['users'] == 3
        assert 'uploads_dir_size' in data['data']

    def test_it_returns_error_if_user_has_no_admin_rights(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.get(
            '/api/stats/all',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)
