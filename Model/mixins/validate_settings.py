from sqlalchemy.orm import validates
from libs.validators.core import model_validator, validate_type_of, validate_range_of, validate_numericality_of
from libs.validators.core import validate_format_of
from libs.validators.string_validators import validate_string_not_empty
from types import BooleanType, UnicodeType


# Again this code needs DRYing
class ValidateSettings(object):
    @validates('speaker_volume')
    @model_validator
    def check_speaker_volume(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 100)
        return int(value)

    @validates('rent_tax_rate', 'sale_tax_rate')
    @model_validator
    def check_tax_rates(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 99.999)
        return float(value)

    @validates('t_day_start', 't_return')
    @model_validator
    def check_times(self, key, value):
        import pytz, datetime
        kiosk_tz = pytz.timezone(self.timezone.name)
        if not isinstance(value, datetime.time):
            from dateutil.parser import parse
            validate_string_not_empty(value)
            time = parse(value)
            return kiosk_tz.localize(time).time()
        else:
            return value

    @validates('tax_jurisdiction')
    @model_validator
    def check_tax_jurisdiction(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_type_of(value, UnicodeType)
        return value

    @validates('reservation_expiration_period')
    @model_validator
    def check_reservation_expiration_period(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 9999)
        return int(value)

    @validates('max_disks_per_card')
    @model_validator
    def check_max_disks_per_card(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 99)
        return int(value)

    @validates('grace_period')
    @model_validator
    def check_grace_period(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 999)
        return int(value)

    @validates('sale_convert_days')
    @model_validator
    def check_sale_convert_days(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 99999)
        return int(value)

    @validates('sale_convert_price')
    @model_validator
    def check_sale_convert_price(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 99999.99)
        return float(value)

    @validates('dvd_preauth_amount', 'blu_ray_preauth_amount', 'game_preauth_amount')
    @model_validator
    def check_preauth_amounts(self, key, value):
        # Here can be None if tariff plan is not with customamount alias
        print value
        if value is not None:
            validate_numericality_of(value)
            validate_range_of(float(value), 0, 99999.99)
            return float(value)
        else:
            return value

    @validates('capture_retry_interval')
    @model_validator
    def check_capture_retry_interval(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 99999)
        return int(value)

    @validates('capture_retry_quantity')
    @model_validator
    def check_capture_retry_quantity(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 999)
        return int(value)

    @validates('terms')
    @model_validator
    def check_terms(self, key, value):
        validate_type_of(value, UnicodeType)
        return value

    @validates('is_bluray_warning', 'is_smart_capture_retry')
    @model_validator
    def check_booleans(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        return bool(int(value))

    @validates('empty_slots_warning')
    @model_validator
    def check_empty_slots_warning(self, key, value):
        if self.__class__.__name__ == 'CompanySettings':
            validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_range_of(float(value), 0, 200)
        return int(value)