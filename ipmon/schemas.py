'''Schemas used for APIs'''
from marshmallow import Schema

class UsersSchema(Schema):
    '''Users schema'''
    class Meta:
        '''Metadata'''
        fields = ('id', 'username', 'password', 'email', 'date_created', 'alerts_enabled')


class HostsSchema(Schema):
    '''Hosts Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'ip_address', 'hostname', 'status', 'last_poll', 'status_change_alert', 'previous_status', 'alerts_enabled')


class PollHistorySchema(Schema):
    '''Poll History Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'host_id', 'poll_time', 'poll_status', 'date_created')


class HostAlertsSchema(Schema):
    '''Host Alerts Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'hostname', 'ip_address', 'host_status', 'poll_time', 'alert_cleared', 'date_created', 'host_id')


class PollingConfigSchema(Schema):
    '''Polling Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'poll_interval', 'history_truncate_days')


class SmtpConfigSchema(Schema):
    '''SMTP Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'smtp_server', 'smtp_port', 'smtp_sender')


class WebThemesSchema(Schema):
    '''Web Theme Schema'''
    class Meta:
        '''Meta'''
        fields = ('id', 'theme_name', 'theme_path', 'active')


class Schemas():
    '''Static methods for accessing schemas'''

    @staticmethod
    def users(many=True):
        """user(s)

        Args:
            many (bool, optional): Return multiple results. Defaults to True.

        Returns:
            UsersSchema: Schema object
        """        
        return UsersSchema(many=many)


    @staticmethod
    def hosts(many=True):
        """host(s)

        Args:
            many (bool, optional): Return multiple results. Defaults to True.

        Returns:
            HostsSchema: Schema object
        """      
        return HostsSchema(many=many)


    @staticmethod
    def poll_history(many=True):
        """poll history

        Args:
            many (bool, optional): Return multiple results. Defaults to True.

        Returns:
            PollHistorySchema: Schema object
        """      
        return PollHistorySchema(many=many)


    @staticmethod
    def host_alerts(many=True):
        """host alerts

        Args:
            many (bool, optional): Return multiple results. Defaults to True.

        Returns:
            HostAlertsSchema: Schema object
        """      
        return HostAlertsSchema(many=many)


    @staticmethod
    def polling_config():
        """smtp config

        Returns:
            PollingConfigSchema: Schema object
        """ 
        return PollingConfigSchema()


    @staticmethod
    def smtp_config():
        """smtp config

        Returns:
            SmtpConfigSchema: Schema object
        """        
        return SmtpConfigSchema()


    @staticmethod
    def web_themes(many=True):
        """web themes

        Args:
            many (bool, optional): Return multiple results. Defaults to True.

        Returns:
            WebThemesSchema: Schema object
        """      
        return WebThemesSchema(many=many)
