# -*- coding: utf-8 -*-
from .address import Address
from .base import Base
from .card import Card
from .company import Company
from .company_kiosk_manager import CompanyKioskManager
from .company_settings import CompanySettings
from .company_settings_to_language import CompanySettingsToLanguage
from .company_site import CompanySite
from .company_social_community import CompanySocialCommunity
from .company_skip_dates import CompanySkipDates
from .company_skip_weekdays import CompanySkipWeekdays
from .company_upc_tariff_plan import CompanyUpcTariffPlan
from .coupon import Coupon
from .coupon_view import CouponView
from .coupon_type import CouponType
from .coupon_usage_info import CouponUsageInfo
from .customer import Customer
from .deal import Deal
from .disk import Disk
from .disk_photo import DiskPhoto
from .featured_movie import FeaturedMovie
from .kiosk import Kiosk
from .kiosk_action import KioskAction
from .kiosk_bash_command import KioskBashCommand
from .kiosk_calibration import KioskCalibration
from .kiosk_screens import KioskScreens
from .kiosk_kiosk_manager import KioskKioskManager
from .kiosk_review import KioskReview
from .kiosk_review_slot import KioskReviewSlot
from .kiosk_settings import KioskSettings
from .kiosk_settings_to_language import KioskSettingsToLanguage
from .kiosk_skip_dates import KioskSkipDates
from .kiosk_skip_weekdays import KioskSkipWeekdays
from .language import Language
from .movie import Movie
from .featured_movie import FeaturedMovie
from .movie_genre import MovieGenre
from .movie_genre_translation import MovieGenreTranslation
from .movie_movie_genre import MovieMovieGenre
from .movie_rating import MovieRating
from .movie_translation import MovieTranslation
from .ordering_list import OrderingList
from .reservation_cart import ReservationCart
from .tariff_plan import TariffPlan
from .tariff_value import TariffValue
from .transaction import Transaction
from .transaction_type import TransactionType
from .upc import UPC
from .upc_movie import UpcMovie
from .upc_sound import UpcSound
from .upc_subtitle import UpcSubtitle
from .update_movies_stats import UpdateMoviesStats
from .update_movies_stats_alt import UpdateMoviesStatsAlt
from .movie_data_load_type import MovieDataLoadType
from .user import User, AnonymousUser
from .user_confirmation_email import UserConfirmationEmail
from .user_restore_password import UserRestorePassword
from .user_type import UserType
from .video_file import VideoFile
from .video_schedule import VideoSchedule
from rep_report import Report
from rep_report_pattern import ReportPattern

from .sys_object import SysObject
from .sys_function import SysFunction
from .user_permission import UserPermission
from .group import Group
from .user_to_group import UserToGroup
from .group_permission import GroupPermission

from .server_data import ServerData
from .slot import Slot

from .movies_view import MoviesView
from .disks_view import DisksView
from .deals_view import DealsView
from .disk_out_30_days_view import DiskOut30DaysView
from .income_30_days_view import Income30DaysView

from .encoder import AlchemyEncoder

from .enumerates import *

from .ps.company_payment_system import CompanyPaymentSystem
from .ps.linkpoint import LinkPoint
from .ps.linkpoint_transactions import LinkpointTransactions
from .ps.firstdata import FirstData
from .ps.firstdata_transactions import FirstdataTransactions
from .ps.payment_system import PaymentSystem

from .jasper_report_template import JaspreReportTemplate

from movie_data_load_status import MovieDataLoadStatus

__author__ = 'D.Ivanets'

items = {value.__tablename__: value for key, value in locals().items() if hasattr(value, '__tablename__')}