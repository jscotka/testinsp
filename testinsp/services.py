from testinsp.base import TestInspector
from testinsp.constants import YAML, STORE_PATH


class ServiceInfo(TestInspector):
    store_type = YAML
    _get_data_command = "systemctl --type=service --state=running"

    def __init__(
        self,
        filename=None,
        pathname=STORE_PATH,
        external_executor=None,
        exclude_list: list = None,
    ):
        super().__init__(
            filename=filename,
            pathname=pathname,
            external_executor=external_executor,
            exclude_list=exclude_list,
        )
        self.exclude_list += ["NetworkManager-dispatcher"]

    def get_data(self):
        raw_data = self.run(self._get_data_command).splitlines()
        removed_header_footer = [item.strip() for item in raw_data[1:-5]]
        removed_header_footer.sort()
        output = dict()
        for service_item in removed_header_footer:
            if len(service_item) > 5:
                service, description = service_item.split(maxsplit=1)
                output[service.strip()] = " ".join(description.strip().split())
        return output
