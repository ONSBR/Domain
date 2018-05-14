from model.persistence import Persistence
from model.domain import *
from sdk import process_memory, event_manager, process_instance
from mapper.builder import MapBuilder
from dateutil import parser
from datetime import datetime
import pytz
import log


class BatchPersistence:

    def __init__(self,session):
        self.session = session

    def get_head_of_process_memory(self, instance_id):
        return process_memory.head(instance_id)

    def extract_head(self, head):
        self.event = head.get("event",{})
        self.instance_id = head.get("instanceId")
        self.process_id = head.get("processId")
        self.system_id = head.get("systemId")
        self.fork = head.get("fork")
        if "map" in head:
            self.map = {
                "map": head["map"].get("content",{}),
                "app_name": head["map"]["name"]
            }
            self.mapper = MapBuilder().build_from_map(self.map)
        else:
            self.map = {}
        if "dataset" in head:
            self.entities = head["dataset"].get("entities",[])
        else:
            self.entities = []
        self.event_out = head.get("eventOut","system.persist.eventout.undefined")

    def get_items_to_persist(self, entities, instance_id):
        """ process head and collect data to persist on domain """
        items = []
        for entity in entities:
            for item in entities[entity]:
                if not self.has_change_track(item):
                    continue
                domain_obj = self.mapper.translator.to_domain(self.map["app_name"], item)
                domain_obj["meta_instance_id"] = instance_id
                domain_obj["branch"] = item["_metadata"].get("branch", "master")
                domain_obj["from_id"] = item.get("fromId")
                domain_obj["modified"] = item["_metadata"].get("modified_at", datetime.utcnow())
                items.append(domain_obj)
        return items


    def has_change_track(self, item):
        return "_metadata" in item and "changeTrack" in item['_metadata']


    def run(self, instance_id):
        try:
            log.info(f"getting data from process memory with instance id {instance_id}")
            head = self.get_head_of_process_memory(instance_id)
            log.info("extracting data from dataset")
            self.extract_head(head)
            log.info("getting items to persist")
            items = self.get_items_to_persist(self.entities, instance_id)
            log.info(f"should persist {len(items)} objects in database")
            self.persist(items)
            log.info("objects persisted")
            parts = self.event["name"].split(".")
            parts.pop()
            parts.append("done")
            name = ".".join(parts)
            log.info(f"pushing event {name} to event manager")
            event_manager.push({"name":self.event_out, "instanceId":instance_id, "payload":{"instance_id":instance_id}})
        except Exception as e:
            event_manager.push({"name":"system.process.persist.error", "instanceId":instance_id, "payload":{"instance_id":instance_id, "origin":self.event}})
            log.info("exception occurred")
            log.critical(e)


    def persist(self, items):
        """
        Identificar qual o b

        """
        processes = self.get_impacted_processes(items)
        if len(processes) > 0:
            log.info(f"Reprocessing {len(processes)} instances")

        log.info(processes)
        repository = Persistence(self.session)
        instances = repository.persist(items)
        repository.commit()

    def get_impacted_processes(self, items):
        older_data = pytz.UTC.localize(datetime.utcnow())
        log.info(older_data)
        impacted_domain = set()
        for item in items:
            if "modified_at" in item["_metadata"]:
                date = parser.parse(item["_metadata"]["modified_at"])
            else:
                date = pytz.UTC.localize(datetime.utcnow())
            if date < older_data:
                older_data = date
            impacted_domain.add(item["_metadata"]["type"])



        log.info(impacted_domain)
        log.info(f"Older data at {older_data}")
        return process_instance.ProcessInstance().get_processes_after(older_data)

