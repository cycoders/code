from k8s_manifest_auditor.rules import no_latest_image_tag, privileged_container, Issue


def test_no_latest_image_tag():
    manifest = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"image": "nginx:latest"}]
                }
            }
        }
    }
    issues = no_latest_image_tag(manifest, "test")
    assert len(issues) == 1
    assert issues[0].severity == "MEDIUM"


def test_privileged_container():
    manifest = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"securityContext": {"privileged": True}}]
                }
            }
        }
    }
    issues = privileged_container(manifest, "test")
    assert len(issues) == 1
    assert issues[0].severity == "HIGH"


def test_no_issues_good_manifest():
    manifest = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"image": "nginx:1.25.3", "securityContext": {"runAsNonRoot": True}}]
                }
            }
        }
    }
    issues = no_latest_image_tag(manifest, "test")
    assert len(issues) == 0