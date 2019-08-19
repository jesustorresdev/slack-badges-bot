import logging
import json
import traceback
import sys
import mimetypes
from aiohttp import web

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.award import AwardService
from slack_badges_bot.services.issuer import IssuerService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.utils.openbadges import OpenBadges

class OpenBadgesWebService:
    def __init__(self, config: ConfigService,
            badge_service: BadgeService,
            award_service: AwardService,
            issuer_service: IssuerService):
        self.config = config
        self.badge_service = badge_service
        self.award_service = award_service
        self.issuer_service = issuer_service
        self.app = web.Application()
        self.openbadges = OpenBadges(config)
        self._setup_routes()
        logging.debug('Started OPENBADGESAWARENLASKDFJ')

    async def badge_handler(self, request):
        try:
            logging.debug('LLEGA REQUESST')
            badge_id = request.match_info['badge_id']
            requested_data = request.match_info['requested_data']
            badge = self.badge_service.retrieve(badge_id)
            if requested_data == 'image':
                image_fd = self.badge_service.open_image(badge)
                content_type = mimetypes.guess_type(f'file.{badge.image.suffix}')[0]
                response = web.Response(body=image_fd.read(), content_type=content_type)
            elif requested_data == 'json':
                badge_class = self.openbadges.badge_class(badge)
                response = web.json_response(badge_class)
            elif requested_data == 'criteria':
                response = web.json_response({'criteria': badge.criteria})
            else:
                response = web.HTTPBadRequest()
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPInternalServerError()
        return response

    async def award_handler(self, request: web.Request):
        try:
            award_id = request.match_info['award_id']
            requested_data = request.match_info['requested_data']
            award = self.award_service.retrieve(award_id)
            logging.debug(award)
            if requested_data == 'json':
                badge_assertion = self.openbadges.badge_assertion(award)
                response = web.json_response(badge_assertion)
            elif requested_data == 'image':
                image_fd = self.award_service.open_image(award)
                content_type = mimetypes.guess_type(f'file.{award.image.suffix}')[0]
                response = web.Response(body=image_fd.read(), content_type=content_type)
            else:
                response = web.HTTPBadRequest()
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPInternalServerError()
        return response

    async def issuer_handler(self, request):
# Este método devuelve el JSON con la info del issuer
        try:
            issuer = self.issuer_service.retrieve(self.config['ISSUER_ID'])
            issuer_organization = self.openbadges.issuer_organization(issuer)
            logging.debug(issuer_organization)
            response = web.json_response(issuer_organization)
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPInternalServerError()
        return response

    async def revocation_handler(self, request: web.Request):
        issuer = self.issuer_service.retrieve(self.config['ISSUER_ID'])
        return web.json_response(issuer.revocationList)

    def _setup_routes(self):
        self.app.router.add_get('/badges/{badge_id}/{requested_data}', self.badge_handler)
        self.app.router.add_get('/issuer', self.issuer_handler)
        self.app.router.add_get('/awards/{award_id}/{requested_data}', self.award_handler)
        self.app.router.add_get('/revocation', self.revocation_handler)

