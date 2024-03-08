class ClubsServiceAdapter:

    @property
    def interface(self):
        from nw_clubs.app_interfaces.service_interface import \
            ServiceInterface
        return ServiceInterface()

    def update_user_club_leaderboards(
            self, user_id: str, resource_value: float,
            resource_name_enum: str):
        self.interface.update_user_resource_value_to_club_leaderboards(
            user_id, resource_name_enum, resource_value)
